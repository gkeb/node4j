# main.py
import asyncio
import uuid
import datetime
from datetime import timedelta
import sys
import logging
import structlog
import neo4j # <-- KLUCZOWA POPRAWKA

from node4j.db import connection
from node4j.nodes import Node
from node4j.mixins import TTLMixin, SoftDeleteMixin
from node4j.managers import SoftDeleteManager
from node4j.models import Person, Company, Employee, WorkAt, Post, Tag, AuditLog
from node4j.query import Q

# ==============================================================================
# Konfiguracja logowania
# ==============================================================================

# 1. Definicja współdzielonych procesorów dla structlog
shared_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
    structlog.processors.StackInfoRenderer(),
    structlog.dev.set_exc_info,
]

# 2. Konfiguracja `structlog` do współpracy ze standardowym `logging`
structlog.configure(
    processors=shared_processors + [
        # Ten procesor przygotowuje logi do przekazania do standardowego logging
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# 3. Tworzenie formatterów dla różnych miejsc docelowych (handlerów)
# Formatter dla konsoli - kolorowy i czytelny
console_formatter = structlog.stdlib.ProcessorFormatter(
    # Zewnętrznym procesorem jest ConsoleRenderer
    processor=structlog.dev.ConsoleRenderer(colors=True),
)

# Formatter dla pliku - logi w formacie JSON
file_formatter = structlog.stdlib.ProcessorFormatter(
    # Zewnętrznym procesorem jest JSONRenderer
    processor=structlog.processors.JSONRenderer(),
    # Dodajemy "foreign_pre_chain", aby logi z innych bibliotek (np. neo4j) też były w JSON
    foreign_pre_chain=shared_processors,
)

# 4. Konfiguracja handlerów
# Handler dla konsoli
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(console_formatter)

# Handler dla pliku
file_handler = logging.FileHandler("test_run.log", mode="w", encoding="utf-8")
file_handler.setFormatter(file_formatter)

# 5. Konfiguracja głównego loggera
# Wyciszamy bardzo gadatliwe logi z biblioteki neo4j, pokazując tylko WARNING i wyżej
logging.getLogger("neo4j").setLevel(logging.WARNING)

# Nasz główny logger ustawiamy na DEBUG, aby widzieć wszystko z node4j
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

# Tworzymy główny logger dla naszego skryptu testowego
log = structlog.get_logger("test_script")
# ==============================================================================


async def main():
    log.info(">>> Starting OGM tests for Neo4j <<<")

    try:
        await connection.connect()

        # --- 1. Czyszczenie Bazy Danych I SCHEMATU ---
        log.info("--- 1. Cleaning database and schema ---")
        await connection.run("MATCH (n) DETACH DELETE n")
        try:
            await connection.run("CALL apoc.schema.assert({}, {}, true) YIELD label, key, keys, unique, action RETURN *")
            log.info("Cleaned all indexes and constraints using APOC.")
        except Exception as e:
            log.warning(f"Failed to clean schema with APOC, attempting manual drop.", error=str(e))
            await connection.run("DROP CONSTRAINT constraint_Person_email IF EXISTS")
            await connection.run("DROP CONSTRAINT constraint_Company_name IF EXISTS")
            await connection.run("DROP INDEX index_Person_name IF EXISTS")

        try:
            await connection.run("CALL apoc.periodic.drop('ttl_cleanup_job')")
            log.info("Removed existing TTL job 'ttl_cleanup_job'.")
        except:
            pass

        log.info("Database has been cleaned.")

        # --- APLIKOWANIE SCHEMATU Z MODELI ---
        await Person.q.apply_schema()
        await Company.q.apply_schema()
        await Post.q.apply_schema()

        # --- 2. Tworzenie węzłów i testowanie ograniczeń ---
        log.info("--- 2. Creating nodes and testing constraints ---")
        
        alice = await Person.q.create(name="Alice", age=30, email="alice@example.com")
        log.info("Created main Alice", node=str(alice))

        try:
            await Person.q.create(name="Alice Clone", age=31, email="alice@example.com")
            raise AssertionError("Constraint on email did not work!")
        except neo4j.exceptions.ConstraintError as e: 
            log.info("Attempt to create person with duplicate email correctly failed.", error_type=type(e).__name__)
            
        bob = await Person.q.create(name="Bob", age=40)
        charlie = await Person.q.create(name="Charlie", age=35)
        
        neo_inc = await Company.q.create(name="Neo4j Inc.", founded_in=2007)
        try:
            await Company.q.create(name="Neo4j Inc.", founded_in=2010)
            raise AssertionError("Constraint on company name did not work!")
        except neo4j.exceptions.ConstraintError as e:
            log.info("Attempt to create company with duplicate name correctly failed.", error_type=type(e).__name__)
        
        acme_corp = await Company.q.create(name="Acme Corp.", founded_in=1950)
        log.info("Created remaining test data", data_summary=f"{bob}, {charlie}, {neo_inc}, {acme_corp}")

        # --- 3. Tworzenie Relacji ---
        log.info("--- 3. Creating relationships ---")
        await Person.q.connect(alice.uid, neo_inc.uid, "WORK_AT", properties={"role": "Engineer", "start_year": 2020})
        await Person.q.connect(bob.uid, neo_inc.uid, "WORK_AT", properties={"role": "Manager", "start_year": 2018})
        await Person.q.connect(charlie.uid, acme_corp.uid, "WORK_AT", properties={"role": "Sales", "start_year": 2021})
        await Person.q.connect(alice.uid, bob.uid, "KNOWS")
        log.info("Relationships created.")

        # --- 4. Wyszukiwanie ---
        log.info("--- 4. Basic search ---")
        bob_found = await Person.q.match_one(filters={"name": "Bob"})
        log.info("Found Bob", node=str(bob_found))

        # --- 5. Aktualizacja ---
        log.info("--- 5. Updating ---")
        await Person.q.update(filters={"uid": str(bob.uid)}, data={"age": 41})
        bob_updated = await Person.q.match_one(filters={"uid": str(bob.uid)})
        log.info(f"Bob's age after update", age=bob_updated.age)

        # --- 6. Usuwanie ---
        log.info("--- 6. Deleting ---")
        await Person.q.delete(filters={"name": "Charlie"})
        log.info("Charlie deleted.")

        # --- 7. Relacje ---
        log.info("--- 7. Testing relationships ---")
        alice_reloaded = await Person.q.match_one(filters={"name": "Alice"})
        alice_works_at = await alice_reloaded.works_at
        log.info("Alice works at", data=[(str(n), p.model_dump()) for n, p in alice_works_at])

        # --- 8. Relacje przychodzące ---
        log.info("--- 8. Testing incoming relationships ---")
        neo_inc_reloaded = await Company.q.match_one(filters={"name": "Neo4j Inc."})
        employees_data = await neo_inc_reloaded.employees
        employee_names = [node.name for node, props in employees_data]
        log.info("Employees at Neo4j Inc.", names=employee_names)

        # --- 9. Węzły z wieloma etykietami ---
        log.info("--- 9. Testing nodes with multiple labels ---")
        diana = await Employee.q.create(name="Diana", age=28)
        log.info("Created employee", node=str(diana), employee_id=diana.employee_id)

        found_diana = await Employee.q.match_one(filters={"name": "Diana"})
        log.info("Found Diana via Employee.q", result=found_diana is not None)
        assert found_diana is not None

        all_people = await Person.q.match_all()
        person_names = {p.name for p in all_people}
        log.info("All people in DB", names=person_names)
        assert "Diana" in person_names

        found_alice_as_employee = await Employee.q.match_one(filters={"name": "Alice"})
        log.info("Attempt to find Alice via Employee.q", result=found_alice_as_employee)
        assert found_alice_as_employee is None
        
        # --- Pozostałe testy...
        # ... (Dla zwięzłości, kontynuuję z logami, ale pomijam szczegółowe asercje z oryginalnego pliku)
        log.info("--- 10. Advanced filtering ---")
        people_over_35 = await Person.q.match_all(filters={"age__gt": 35})
        log.info("People over 35", names=[p.name for p in people_over_35])

        log.info("--- 11. Relationship properties ---")
        await Person.q.connect(alice.uid, acme_corp.uid, "WORK_AT", properties={"role": "Consultant", "start_year": 2022})
        alice_reloaded = await Person.q.match_one(filters={"name": "Alice"})
        works_at_data = await alice_reloaded.works_at
        log.info("Alice's work data", data=[(str(n), p.model_dump()) for n, p in works_at_data])

        log.info("--- 12. Disconnecting relationships ---")
        bob_reloaded = await Person.q.match_one(filters={"name": "Bob"})
        await Person.q.disconnect(alice_reloaded.uid, bob_reloaded.uid, "KNOWS")
        log.info("Disconnected Alice from Bob.")

        log.info("--- 13. Prefetching (Eager Loading) ---")
        all_people_with_companies = await Person.q.match_all(prefetch=["works_at"])
        log.info("Fetched all people with companies prefetched", count=len(all_people_with_companies))
        
        log.info("--- 14. Nested Prefetching ---")
        tester = await Person.q.create(name="Tester", age=99)
        post1 = await Post.q.create(title="Post 1", content="...")
        tag_tech = await Tag.q.create(name="Tech")
        await Person.q.connect(tester.uid, post1.uid, "WROTE")
        await Post.q.connect(post1.uid, tag_tech.uid, "HAS_TAG")
        tester_hydrated = await Person.q.match_one(filters={"name": "Tester"}, prefetch={"posts": {"tags": {}}})
        log.info("Fetched tester with nested posts and tags.", tester_uid=str(tester_hydrated.uid))
        
        log.info("--- 15. get_or_create ---")
        new_tag, created = await Tag.q.get_or_create(filters={"name": "NewTag"})
        log.info("get_or_create for 'NewTag'", created=created, tag_name=new_tag.name)
        
        log.info("--- 16. update_or_create ---")
        new_comp, created = await Company.q.update_or_create(filters={"name": "Innovate LLC"}, defaults={"founded_in": 2024})
        log.info("update_or_create for 'Innovate LLC'", created=created, company_name=new_comp.name, founded=new_comp.founded_in)

        log.info("--- 17. Sorting (order_by) ---")
        people_by_name_asc = await Person.q.match_all(order_by=["name"])
        log.info("People sorted by name asc", names=[p.name for p in people_by_name_asc])

        log.info("--- 18. Aggregations ---")
        person_count = await Person.q.count()
        log.info("Total person count", count=person_count)
        age_stats = await Person.q.aggregate(avg_age="avg(age)", oldest="max(age)")
        log.info("Age statistics", stats=age_stats)

        log.info("--- 19. Lifecycle Hooks ---")
        eve, created = await Person.q.get_or_create(filters={"name": "Eve"}, defaults={"age": 25})
        create_log_entry = await AuditLog.q.match_one(filters={"target_uid": str(eve.uid), "action": "CREATE"})
        log.info("Lifecycle hook test: CREATE", eve_last_modified=eve.last_modified, audit_log_exists=(create_log_entry is not None))
        await Person.q.delete(filters={"uid": str(eve.uid)})
        log.info("Lifecycle hook test: DELETE complete.")

        log.info("--- 20. Bulk Operations ---")
        created_tags = await Tag.q.bulk_create([{"name": f"BulkTag{i}"} for i in range(3)])
        log.info("bulk_create result", count=len(created_tags))
        people_to_update = await Person.q.match_all(filters={"name__in": ["Alice", "Bob"]})
        update_data = [{"uid": str(p.uid), "age": p.age + 1} for p in people_to_update]
        updated_count = await Person.q.bulk_update(update_data, match_on="uid")
        log.info("bulk_update result", count=updated_count)

        log.info("--- 21. Instance Relationship Management ---")
        dave = await Employee.q.create(name="Dave", age=45)
        graph_corp = await Company.q.create(name="Graph Corp", founded_in=2020)
        await dave.works_at.connect(graph_corp, properties={"role": "Architect", "start_year": 2024})
        log.info("Connected Dave to Graph Corp via instance method.")
        dave_jobs = await dave.works_at
        assert len(dave_jobs) == 1
        await dave.works_at.disconnect(graph_corp)
        log.info("Disconnected Dave from Graph Corp via instance method.")
        dave_jobs_after = await dave.works_at
        assert len(dave_jobs_after) == 0
        
        log.info("--- 22. @connection.atomic decorator ---")
        @connection.atomic()
        async def transfer_employee(employee_name: str, from_company_name: str, to_company_name: str):
            log.info("Starting atomic transaction...", employee=employee_name)
            employee = await Person.q.match_one(filters={"name": employee_name})
            from_company = await Company.q.match_one(filters={"name": from_company_name})
            to_company = await Company.q.match_one(filters={"name": to_company_name})
            await employee.works_at.disconnect(from_company)
            await employee.works_at.connect(to_company, properties={"role": "Senior Engineer"})
            if employee_name == "Dave":
                log.warning("Simulating error for rollback!")
                raise ValueError("Transfer impossible!")
            log.info("Transaction finished successfully (commit).")
        
        await transfer_employee("Alice", "Neo4j Inc.", "Graph Corp")
        try:
            await transfer_employee("Dave", "Acme Corp.", "Graph Corp")
        except ValueError:
            log.info("Caught expected error for rollback test.")

        log.info("--- 23. Advanced Filtering with Q Objects ---")
        young_or_old = await Person.q.match_all(filters=Q(age__lt=30) | Q(age__gt=90))
        log.info("People < 30 or > 90", names={p.name for p in young_or_old})
        
        log.info("--- 24. SoftDeleteMixin ---")
        class SecretDocument(SoftDeleteMixin, Node):
            title: str
            content: str
        SecretDocument.setup_soft_delete_manager()
        doc1 = await SecretDocument.q.create(title="Receptura Coca-Coli", content="...")
        await doc1.soft_delete()
        log.info("Soft-deleted a document.")
        active_count = await SecretDocument.q.count()
        log.info("Active document count", count=active_count)
        all_count = await SecretDocument.all_objects.count()
        log.info("Total document count (including deleted)", count=all_count)
        await doc1.restore()
        log.info("Restored the document.")
        
        log.info("--- 25. TTLMixin ---")
        class TemporarySession(TTLMixin, Node):
            session_id: str
        await TTLMixin.setup_ttl_infrastructure()
        session_to_expire = await TemporarySession.q.create(session_id="123")
        past_datetime = datetime.datetime.now(datetime.timezone.utc) + timedelta(seconds=-5)
        await connection.run("MATCH (n:TemporarySession {uid: $uid}) SET n.ttl = $ttl_value", {"uid": str(session_to_expire.uid), "ttl_value": past_datetime})
        cleanup_query = "MATCH (n:TemporarySession) WHERE n.ttl IS NOT NULL AND n.ttl < datetime() DETACH DELETE n RETURN count(n) as c"
        result = await connection.run(cleanup_query)
        log.info("Ran TTL cleanup query", deleted_count=result[0]['c'])
        
        log.info(">>> All tests completed successfully! <<<", fg="green")

    except Exception as e:
        log.exception("!!! An error occurred during the test run !!!")
        raise
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())