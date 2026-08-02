"""Test data factories for generating consistent test objects."""
import uuid


def _uid():
    return uuid.uuid4().hex[:8]


class UserFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "email": f"user_{uid}@test.edu",
            "password": "TestPass123!",
            "full_name": f"Test User {uid}",
            "institution": "Test University",
            "department": "Plant Science",
        }
        defaults.update(overrides)
        return defaults


class ProjectFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "name": f"Project {uid}",
            "description": f"Description for project {uid}",
            "tags": ["test", "plant-science"],
        }
        defaults.update(overrides)
        return defaults


class SpeciesFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "scientific_name": f"Speciesus testus {uid}",
            "common_name": f"Test Plant {uid}",
            "family": "Testaceae",
            "genus": "Speciesus",
        }
        defaults.update(overrides)
        return defaults


class AccessionFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "accession_number": f"ACC-{uid}",
            "name": f"Accession {uid}",
            "species_name": "Triticum aestivum",
            "origin_country": "USA",
            "collection_year": 2024,
            "status": "active",
        }
        defaults.update(overrides)
        return defaults


class SequenceFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "name": f"Gene_{uid}",
            "sequence": "ATGCGATCGATCGATCGATCG" * 5,
            "sequence_type": "gene",
            "species_name": "Triticum aestivum",
            "description": f"Test sequence {uid}",
        }
        defaults.update(overrides)
        return defaults


class VariantFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "name": f"SNP_{uid}",
            "chromosome": "1A",
            "position": 12345,
            "reference_allele": "A",
            "alternative_allele": "T",
            "variant_type": "SNP",
            "quality": 30.0,
        }
        defaults.update(overrides)
        return defaults


class ExperimentFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "name": f"Experiment {uid}",
            "description": f"Test experiment {uid}",
            "experiment_type": "greenhouse",
            "status": "planning",
        }
        defaults.update(overrides)
        return defaults


class TraitFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "name": f"Trait_{uid}",
            "description": f"Phenotype trait {uid}",
            "trait_type": "quantitative",
            "unit": "cm",
        }
        defaults.update(overrides)
        return defaults


class MeasurementFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "trait_name": f"Trait_{uid}",
            "accession_number": f"ACC-{uid}",
            "value": 42.5,
            "replicate": 1,
        }
        defaults.update(overrides)
        return defaults


class MolecularExperimentFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "name": f"PCR_{uid}",
            "description": f"Molecular experiment {uid}",
            "experiment_type": "pcr",
            "status": "planning",
        }
        defaults.update(overrides)
        return defaults


class PrimerFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "name": f"Primer_{uid}",
            "sequence_5to3": "ATCGATCGATCGATCG",
            "primer_type": "forward",
            "target_gene": f"Gene_{uid}",
            "melting_temperature": 60.0,
        }
        defaults.update(overrides)
        return defaults


class ConstructFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "name": f"Construct_{uid}",
            "description": f"Test construct {uid}",
            "construct_type": "expression_vector",
            "vector_backbone": "pCAMBIA1300",
        }
        defaults.update(overrides)
        return defaults


class PaperFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "title": f"Research Paper {uid}",
            "authors": [f"Author {uid}"],
            "abstract": f"Abstract for paper {uid}",
            "doi": f"10.1000/{uid}.2024.001",
            "year": 2024,
            "source": "pubmed",
        }
        defaults.update(overrides)
        return defaults


class CollectionFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "name": f"Collection {uid}",
            "description": f"Paper collection {uid}",
        }
        defaults.update(overrides)
        return defaults


class EntityFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "name": f"Entity_{uid}",
            "entity_type": "gene",
            "description": f"KG entity {uid}",
            "properties": {"key": "value"},
        }
        defaults.update(overrides)
        return defaults


class EdgeFactory:
    @staticmethod
    def build(**overrides):
        defaults = {
            "source_entity_id": str(uuid.uuid4()),
            "target_entity_id": str(uuid.uuid4()),
            "relation_type": "REGULATES",
            "properties": {},
        }
        defaults.update(overrides)
        return defaults


class ConversationFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "title": f"Conversation {uid}",
            "description": f"AI conversation {uid}",
        }
        defaults.update(overrides)
        return defaults


class AnalysisJobFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "name": f"Job_{uid}",
            "analysis_type": "alignment",
            "description": f"Analysis job {uid}",
            "input_data": {"file": "sample.fasta"},
        }
        defaults.update(overrides)
        return defaults


class PipelineTemplateFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "name": f"Pipeline_{uid}",
            "analysis_type": "alignment",
            "description": f"Pipeline template {uid}",
            "steps": ["preprocess", "align", "call_variants"],
        }
        defaults.update(overrides)
        return defaults


class ReportFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "title": f"Report {uid}",
            "report_type": "summary",
            "content": f"Report content {uid}",
        }
        defaults.update(overrides)
        return defaults


class ReportTemplateFactory:
    @staticmethod
    def build(**overrides):
        uid = _uid()
        defaults = {
            "name": f"Template_{uid}",
            "report_type": "experiment",
            "description": f"Report template {uid}",
            "sections": ["Introduction", "Methods", "Results"],
        }
        defaults.update(overrides)
        return defaults
