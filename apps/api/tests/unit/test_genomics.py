import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import UTC, datetime

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.modules.genomics.domain.use_cases import (
    BulkCreateVariantsUseCase,
    CreateAnnotationUseCase,
    CreateSequenceUseCase,
    CreateVariantUseCase,
    DeleteAnnotationUseCase,
    DeleteSequenceUseCase,
    DeleteVariantUseCase,
    GetAnnotationUseCase,
    GetSequenceUseCase,
    GetVariantUseCase,
    ListAnnotationsUseCase,
    ListSequencesUseCase,
    ListVariantsUseCase,
    SearchVariantsUseCase,
    UpdateAnnotationUseCase,
    UpdateSequenceUseCase,
)


class TestCreateSequenceUseCase:
    def setup_method(self):
        self.sequence_repo = MagicMock()
        self.use_case = CreateSequenceUseCase(self.sequence_repo)

    @pytest.mark.asyncio
    async def test_create_sequence_success(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        mock_seq.name = "Rice Genome"
        mock_seq.sequence_type = "genome"
        mock_seq.created_at = datetime.now(UTC)
        mock_seq.updated_at = datetime.now(UTC)
        self.sequence_repo.create = AsyncMock(return_value=mock_seq)
        result = await self.use_case.execute(
            name="Rice Genome",
            user_id="user-1",
            sequence_type="genome",
            organism="Oryza sativa",
        )
        assert result.name == "Rice Genome"
        self.sequence_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_sequence_empty_name(self):
        with pytest.raises(ValidationException):
            await self.use_case.execute(name="", user_id="user-1")

    @pytest.mark.asyncio
    async def test_create_sequence_invalid_type(self):
        with pytest.raises(ValidationException):
            await self.use_case.execute(name="Test", user_id="user-1", sequence_type="invalid")

    @pytest.mark.asyncio
    async def test_create_sequence_invalid_gc(self):
        with pytest.raises(ValidationException):
            await self.use_case.execute(name="Test", user_id="user-1", gc_content=1.5)

    @pytest.mark.asyncio
    async def test_create_sequence_invalid_positions(self):
        with pytest.raises(ValidationException):
            await self.use_case.execute(
                name="Test", user_id="user-1",
                start_position=1000, end_position=100,
            )


class TestGetSequenceUseCase:
    def setup_method(self):
        self.sequence_repo = MagicMock()
        self.use_case = GetSequenceUseCase(self.sequence_repo)

    @pytest.mark.asyncio
    async def test_get_sequence_success(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        mock_seq.name = "Test"
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        result = await self.use_case.execute("seq-1")
        assert result.name == "Test"

    @pytest.mark.asyncio
    async def test_get_sequence_not_found(self):
        self.sequence_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("seq-999")


class TestListSequencesUseCase:
    def setup_method(self):
        self.sequence_repo = MagicMock()
        self.use_case = ListSequencesUseCase(self.sequence_repo)

    @pytest.mark.asyncio
    async def test_list_sequences_success(self):
        self.sequence_repo.list_sequences = AsyncMock(return_value=[])
        self.sequence_repo.count_sequences = AsyncMock(return_value=0)
        result = await self.use_case.execute(user_id="user-1")
        assert result["items"] == []
        assert result["total"] == 0


class TestUpdateSequenceUseCase:
    def setup_method(self):
        self.sequence_repo = MagicMock()
        self.use_case = UpdateSequenceUseCase(self.sequence_repo)

    @pytest.mark.asyncio
    async def test_update_sequence_success(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        mock_seq.created_by = "user-1"
        mock_seq.name = "Original"
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        self.sequence_repo.update = AsyncMock(return_value=mock_seq)
        result = await self.use_case.execute("seq-1", "user-1", name="Updated")
        assert result.name == "Updated"

    @pytest.mark.asyncio
    async def test_update_sequence_not_found(self):
        self.sequence_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("seq-999", "user-1", name="X")

    @pytest.mark.asyncio
    async def test_update_sequence_forbidden(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        mock_seq.created_by = "user-2"
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        with pytest.raises(ValidationException):
            await self.use_case.execute("seq-1", "user-1", name="X")

    @pytest.mark.asyncio
    async def test_update_sequence_empty_name(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        mock_seq.created_by = "user-1"
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        with pytest.raises(ValidationException):
            await self.use_case.execute("seq-1", "user-1", name="")

    @pytest.mark.asyncio
    async def test_update_sequence_invalid_type(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        mock_seq.created_by = "user-1"
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        with pytest.raises(ValidationException):
            await self.use_case.execute("seq-1", "user-1", sequence_type="invalid")


class TestDeleteSequenceUseCase:
    def setup_method(self):
        self.sequence_repo = MagicMock()
        self.use_case = DeleteSequenceUseCase(self.sequence_repo)

    @pytest.mark.asyncio
    async def test_delete_sequence_success(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        mock_seq.created_by = "user-1"
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        self.sequence_repo.delete = AsyncMock(return_value=True)
        result = await self.use_case.execute("seq-1", "user-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_sequence_not_found(self):
        self.sequence_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("seq-999", "user-1")

    @pytest.mark.asyncio
    async def test_delete_sequence_forbidden(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        mock_seq.created_by = "user-2"
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        with pytest.raises(ValidationException):
            await self.use_case.execute("seq-1", "user-1")


class TestCreateVariantUseCase:
    def setup_method(self):
        self.variant_repo = MagicMock()
        self.sequence_repo = MagicMock()
        self.use_case = CreateVariantUseCase(self.variant_repo, self.sequence_repo)

    @pytest.mark.asyncio
    async def test_create_variant_success(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        mock_var = MagicMock()
        mock_var.id = "var-1"
        mock_var.created_at = datetime.now(UTC)
        mock_var.updated_at = datetime.now(UTC)
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        self.variant_repo.create = AsyncMock(return_value=mock_var)
        result = await self.use_case.execute(
            sequence_id="seq-1",
            chromosome="1",
            position=12345,
            reference_allele="A",
            alternate_allele="G",
            variant_type="SNP",
            user_id="user-1",
        )
        assert result.id == "var-1"

    @pytest.mark.asyncio
    async def test_create_variant_sequence_not_found(self):
        self.sequence_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute(
                sequence_id="seq-999", chromosome="1", position=1,
                reference_allele="A", alternate_allele="G",
                variant_type="SNP", user_id="user-1",
            )

    @pytest.mark.asyncio
    async def test_create_variant_empty_chromosome(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        with pytest.raises(ValidationException):
            await self.use_case.execute(
                sequence_id="seq-1", chromosome="", position=1,
                reference_allele="A", alternate_allele="G",
                variant_type="SNP", user_id="user-1",
            )

    @pytest.mark.asyncio
    async def test_create_variant_negative_position(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        with pytest.raises(ValidationException):
            await self.use_case.execute(
                sequence_id="seq-1", chromosome="1", position=-1,
                reference_allele="A", alternate_allele="G",
                variant_type="SNP", user_id="user-1",
            )

    @pytest.mark.asyncio
    async def test_create_variant_invalid_type(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        with pytest.raises(ValidationException):
            await self.use_case.execute(
                sequence_id="seq-1", chromosome="1", position=1,
                reference_allele="A", alternate_allele="G",
                variant_type="invalid", user_id="user-1",
            )

    @pytest.mark.asyncio
    async def test_create_variant_invalid_af(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        with pytest.raises(ValidationException):
            await self.use_case.execute(
                sequence_id="seq-1", chromosome="1", position=1,
                reference_allele="A", alternate_allele="G",
                variant_type="SNP", user_id="user-1",
                allele_frequency=1.5,
            )


class TestBulkCreateVariantsUseCase:
    def setup_method(self):
        self.variant_repo = MagicMock()
        self.sequence_repo = MagicMock()
        self.use_case = BulkCreateVariantsUseCase(self.variant_repo, self.sequence_repo)

    @pytest.mark.asyncio
    async def test_bulk_create_success(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        self.variant_repo.bulk_create = AsyncMock(return_value=[MagicMock(), MagicMock()])
        result = await self.use_case.execute(
            sequence_id="seq-1",
            variants_data=[
                {"chromosome": "1", "position": 100, "reference_allele": "A", "alternate_allele": "G", "variant_type": "SNP"},
                {"chromosome": "1", "position": 200, "reference_allele": "C", "alternate_allele": "T", "variant_type": "SNP"},
            ],
            user_id="user-1",
        )
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_bulk_create_empty_data(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        with pytest.raises(ValidationException):
            await self.use_case.execute(sequence_id="seq-1", variants_data=[], user_id="user-1")

    @pytest.mark.asyncio
    async def test_bulk_create_missing_field(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        with pytest.raises(ValidationException):
            await self.use_case.execute(
                sequence_id="seq-1",
                variants_data=[{"chromosome": "1"}],
                user_id="user-1",
            )


class TestGetVariantUseCase:
    def setup_method(self):
        self.variant_repo = MagicMock()
        self.use_case = GetVariantUseCase(self.variant_repo)

    @pytest.mark.asyncio
    async def test_get_variant_success(self):
        mock_var = MagicMock()
        mock_var.id = "var-1"
        self.variant_repo.get_by_id = AsyncMock(return_value=mock_var)
        result = await self.use_case.execute("var-1")
        assert result.id == "var-1"

    @pytest.mark.asyncio
    async def test_get_variant_not_found(self):
        self.variant_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("var-999")


class TestListVariantsUseCase:
    def setup_method(self):
        self.variant_repo = MagicMock()
        self.use_case = ListVariantsUseCase(self.variant_repo)

    @pytest.mark.asyncio
    async def test_list_variants_success(self):
        self.variant_repo.list_by_sequence = AsyncMock(return_value=[])
        self.variant_repo.count_by_sequence = AsyncMock(return_value=0)
        result = await self.use_case.execute(sequence_id="seq-1")
        assert result["items"] == []
        assert result["total"] == 0


class TestSearchVariantsUseCase:
    def setup_method(self):
        self.variant_repo = MagicMock()
        self.use_case = SearchVariantsUseCase(self.variant_repo)

    @pytest.mark.asyncio
    async def test_search_variants_success(self):
        self.variant_repo.search = AsyncMock(return_value=[])
        result = await self.use_case.execute(sequence_id="seq-1", chromosome="1")
        assert result["items"] == []


class TestDeleteVariantUseCase:
    def setup_method(self):
        self.variant_repo = MagicMock()
        self.use_case = DeleteVariantUseCase(self.variant_repo)

    @pytest.mark.asyncio
    async def test_delete_variant_success(self):
        mock_var = MagicMock()
        mock_var.id = "var-1"
        self.variant_repo.get_by_id = AsyncMock(return_value=mock_var)
        self.variant_repo.delete = AsyncMock(return_value=True)
        result = await self.use_case.execute("var-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_variant_not_found(self):
        self.variant_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("var-999")


class TestCreateAnnotationUseCase:
    def setup_method(self):
        self.annotation_repo = MagicMock()
        self.sequence_repo = MagicMock()
        self.use_case = CreateAnnotationUseCase(self.annotation_repo, self.sequence_repo)

    @pytest.mark.asyncio
    async def test_create_annotation_success(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        mock_ann = MagicMock()
        mock_ann.id = "ann-1"
        mock_ann.created_at = datetime.now(UTC)
        mock_ann.updated_at = datetime.now(UTC)
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        self.annotation_repo.search_by_gene = AsyncMock(return_value=None)
        self.annotation_repo.create = AsyncMock(return_value=mock_ann)
        result = await self.use_case.execute(
            sequence_id="seq-1",
            gene_symbol="Os01g0100100",
            user_id="user-1",
            gene_name="LOC_Os01g0100100",
        )
        assert result.id == "ann-1"

    @pytest.mark.asyncio
    async def test_create_annotation_sequence_not_found(self):
        self.sequence_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute(
                sequence_id="seq-999", gene_symbol="Gene1", user_id="user-1",
            )

    @pytest.mark.asyncio
    async def test_create_annotation_empty_gene_symbol(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        with pytest.raises(ValidationException):
            await self.use_case.execute(
                sequence_id="seq-1", gene_symbol="", user_id="user-1",
            )

    @pytest.mark.asyncio
    async def test_create_annotation_already_exists(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        mock_existing = MagicMock()
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        self.annotation_repo.search_by_gene = AsyncMock(return_value=mock_existing)
        with pytest.raises(ConflictException):
            await self.use_case.execute(
                sequence_id="seq-1", gene_symbol="Gene1", user_id="user-1",
            )

    @pytest.mark.asyncio
    async def test_create_annotation_invalid_strand(self):
        mock_seq = MagicMock()
        mock_seq.id = "seq-1"
        self.sequence_repo.get_by_id = AsyncMock(return_value=mock_seq)
        self.annotation_repo.search_by_gene = AsyncMock(return_value=None)
        with pytest.raises(ValidationException):
            await self.use_case.execute(
                sequence_id="seq-1", gene_symbol="Gene1", user_id="user-1",
                strand="x",
            )


class TestGetAnnotationUseCase:
    def setup_method(self):
        self.annotation_repo = MagicMock()
        self.use_case = GetAnnotationUseCase(self.annotation_repo)

    @pytest.mark.asyncio
    async def test_get_annotation_success(self):
        mock_ann = MagicMock()
        mock_ann.id = "ann-1"
        self.annotation_repo.get_by_id = AsyncMock(return_value=mock_ann)
        result = await self.use_case.execute("ann-1")
        assert result.id == "ann-1"

    @pytest.mark.asyncio
    async def test_get_annotation_not_found(self):
        self.annotation_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("ann-999")


class TestListAnnotationsUseCase:
    def setup_method(self):
        self.annotation_repo = MagicMock()
        self.use_case = ListAnnotationsUseCase(self.annotation_repo)

    @pytest.mark.asyncio
    async def test_list_annotations_success(self):
        self.annotation_repo.list_by_sequence = AsyncMock(return_value=[])
        self.annotation_repo.count_by_sequence = AsyncMock(return_value=0)
        result = await self.use_case.execute(sequence_id="seq-1")
        assert result["items"] == []
        assert result["total"] == 0


class TestUpdateAnnotationUseCase:
    def setup_method(self):
        self.annotation_repo = MagicMock()
        self.use_case = UpdateAnnotationUseCase(self.annotation_repo)

    @pytest.mark.asyncio
    async def test_update_annotation_success(self):
        mock_ann = MagicMock()
        mock_ann.id = "ann-1"
        mock_ann.gene_name = "Original"
        self.annotation_repo.get_by_id = AsyncMock(return_value=mock_ann)
        self.annotation_repo.update = AsyncMock(return_value=mock_ann)
        result = await self.use_case.execute("ann-1", gene_name="Updated")
        assert result.gene_name == "Updated"

    @pytest.mark.asyncio
    async def test_update_annotation_not_found(self):
        self.annotation_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("ann-999", gene_name="X")


class TestDeleteAnnotationUseCase:
    def setup_method(self):
        self.annotation_repo = MagicMock()
        self.use_case = DeleteAnnotationUseCase(self.annotation_repo)

    @pytest.mark.asyncio
    async def test_delete_annotation_success(self):
        mock_ann = MagicMock()
        mock_ann.id = "ann-1"
        self.annotation_repo.get_by_id = AsyncMock(return_value=mock_ann)
        self.annotation_repo.delete = AsyncMock(return_value=True)
        result = await self.use_case.execute("ann-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_annotation_not_found(self):
        self.annotation_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await self.use_case.execute("ann-999")
