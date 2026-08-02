import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm import get_llm

logger = structlog.get_logger()

IMAGE_SYSTEM_PROMPT = """You are PIP Image Analysis Assistant, an expert in plant image analysis and phenomics.

You can analyze plant images for:
- Disease detection and severity assessment
- Growth stage classification
- Morphological measurements
- Color analysis and health indicators
- Leaf area estimation
- Root architecture analysis
- Seed counting and quality assessment

Rules:
- Provide quantitative measurements when possible
- Describe confidence levels for classifications
- Note image quality limitations
- Recommend appropriate analysis methods
- Be specific about what can be measured from the image"""


async def analyze_plant_image(
    image_url: str,
    analysis_type: str = "comprehensive",
    species: str | None = None,
    context: dict | None = None,
) -> dict:
    """Analyze a plant image using AI vision capabilities."""
    llm = get_llm()

    species_str = f"Species: {species}" if species else "Species: Unknown"

    prompt = f"""Analyze this plant image: {image_url}

{analysis_type} analysis requested.
{species_str}

Provide:
1. Overall health assessment
2. Visible symptoms or features
3. Growth stage estimation
4. Morphological observations
5. Color analysis
6. Any signs of stress, disease, or deficiency
7. Recommended measurements for this image type
8. Confidence level for each assessment

If quantitative measurements are possible, provide estimates with units.
Note any limitations due to image quality or angle."""

    messages = [
        SystemMessage(content=IMAGE_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    try:
        response = await llm.ainvoke(messages)
        return {
            "analysis": response.content,
            "image_url": image_url,
            "analysis_type": analysis_type,
            "species": species,
        }
    except Exception as e:
        logger.error("image_analysis_failed", error=str(e))
        return {
            "analysis": "Unable to analyze image at this time.",
            "image_url": image_url,
        }


async def classify_plant_disease(
    image_url: str,
    species: str | None = None,
) -> dict:
    """Classify plant disease from an image."""
    llm = get_llm()

    species_str = f"Species: {species}" if species else "Species: Unknown"

    prompt = f"""Classify the disease or health condition in this plant image: {image_url}

{species_str}

Provide:
1. Primary diagnosis (most likely condition)
2. Differential diagnoses (alternatives)
3. Confidence level (High/Medium/Low)
4. Symptoms observed
5. Pathogen or cause (if identifiable)
6. Severity assessment (mild/moderate/severe)
7. Recommended confirmation tests
8. Suggested management approaches

Be specific and use standard plant pathology terminology.
Clearly state if the image quality limits your analysis."""

    messages = [
        SystemMessage(content=IMAGE_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    try:
        response = await llm.ainvoke(messages)
        return {
            "classification": response.content,
            "image_url": image_url,
            "species": species,
        }
    except Exception as e:
        logger.error("disease_classification_failed", error=str(e))
        return {
            "classification": "Unable to classify image.",
            "image_url": image_url,
        }


async def measure_phenotype(
    image_url: str,
    measurements: list[str] | None = None,
    scale_reference: str | None = None,
) -> dict:
    """Estimate phenotypic measurements from an image."""
    llm = get_llm()

    measure_str = "All measurable traits" if not measurements else ", ".join(measurements)
    scale_str = f"Scale reference: {scale_reference}" if scale_reference else "No scale reference provided"

    prompt = f"""Estimate phenotypic measurements from this plant image: {image_url}

Requested measurements: {measure_str}
{scale_str}

Provide estimates for any measurable traits including:
1. Plant height (if visible)
2. Leaf area (if visible)
3. Stem diameter (if visible)
4. Leaf count
5. Canopy coverage percentage
6. Color indices (greenness, chlorosis)
7. Root length (if root image)
8. Seed count (if applicable)
9. Fruit size (if applicable)

For each measurement:
- Provide numerical estimate with units
- State confidence level
- Note any assumptions made
- Indicate if scale calibration is needed

Be honest about what cannot be reliably measured from the image."""

    messages = [
        SystemMessage(content=IMAGE_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    try:
        response = await llm.ainvoke(messages)
        return {
            "measurements": response.content,
            "image_url": image_url,
            "requested_measurements": measurements or [],
        }
    except Exception as e:
        logger.error("phenotype_measurement_failed", error=str(e))
        return {
            "measurements": "Unable to measure phenotypes from this image.",
            "image_url": image_url,
        }


async def compare_images(
    image_urls: list[str],
    comparison_focus: str = "morphological",
) -> dict:
    """Compare multiple plant images."""
    llm = get_llm()

    images_str = "\n".join(f"Image {i+1}: {url}" for i, url in enumerate(image_urls))

    prompt = f"""Compare the following plant images:

{images_str}

Comparison focus: {comparison_focus}

Provide:
1. Visual differences observed
2. Morphological comparisons
3. Health status comparison
4. Growth stage differences
5. Color variations
6. Any anomalies in either image
7. Recommendations for further analysis

Be systematic in your comparison."""

    messages = [
        SystemMessage(content=IMAGE_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    try:
        response = await llm.ainvoke(messages)
        return {
            "comparison": response.content,
            "image_count": len(image_urls),
            "focus": comparison_focus,
        }
    except Exception as e:
        logger.error("image_comparison_failed", error=str(e))
        return {
            "comparison": "Unable to compare images at this time.",
            "image_count": len(image_urls),
        }
