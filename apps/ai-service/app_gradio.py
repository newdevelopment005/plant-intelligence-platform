import gradio as gr
import os
import httpx
from datetime import datetime

API_BASE = os.getenv("API_URL", "http://localhost:8001")

async def research_chat(message, history):
    """Chat with the AI Research Assistant."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE}/api/v1/research/chat",
                json={"message": message, "session_id": "gradio-user"}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response received")
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection error: {str(e)}"

async def search_literature(query, max_results=5):
    """Search PubMed for scientific papers."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{API_BASE}/api/v1/literature/search",
                json={"query": query, "max_results": max_results}
            )
            if response.status_code == 200:
                data = response.json()
                papers = data.get("results", [])
                if not papers:
                    return "No papers found."
                output = f"Found {len(papers)} papers:\n\n"
                for i, paper in enumerate(papers, 1):
                    output += f"**{i}. {paper.get('title', 'N/A')}**\n"
                    output += f"   Authors: {paper.get('authors', 'N/A')}\n"
                    output += f"   Journal: {paper.get('journal', 'N/A')} ({paper.get('year', 'N/A')})\n"
                    output += f"   PMID: {paper.get('pmid', 'N/A')}\n\n"
                return output
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection error: {str(e)}"

async def summarize_paper(paper_text):
    """Summarize a scientific paper."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE}/api/v1/literature/summarize",
                json={"text": paper_text}
            )
            if response.status_code == 200:
                data = response.json()
                summary = data.get("summary", "No summary generated")
                key_findings = data.get("key_findings", [])
                output = f"## Summary\n\n{summary}\n\n"
                if key_findings:
                    output += "## Key Findings\n\n"
                    for finding in key_findings:
                        output += f"- {finding}\n"
                return output
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection error: {str(e)}"

async def get_gene_recommendations(phenotype, species="Arabidopsis thaliana"):
    """Get gene recommendations based on phenotype."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE}/api/v1/research/gene-recommendations",
                json={"phenotype": phenotype, "species": species}
            )
            if response.status_code == 200:
                data = response.json()
                genes = data.get("recommendations", [])
                if not genes:
                    return "No gene recommendations found."
                output = f"## Gene Recommendations for: {phenotype}\n\n"
                output += f"**Species**: {species}\n\n"
                for i, gene in enumerate(genes, 1):
                    output += f"### {i}. {gene.get('gene_name', 'N/A')}\n"
                    output += f"- **Function**: {gene.get('function', 'N/A')}\n"
                    output += f"- **Evidence**: {gene.get('evidence', 'N/A')}\n"
                    output += f"- **Confidence**: {gene.get('confidence', 'N/A')}\n\n"
                return output
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection error: {str(e)}"

async def design_experiment(research_question, variables=""):
    """Design a rigorous experiment."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE}/api/v1/research/experiment-design",
                json={
                    "research_question": research_question,
                    "variables": variables.split(",") if variables else []
                }
            )
            if response.status_code == 200:
                data = response.json()
                design = data.get("experiment_design", {})
                output = "## Experiment Design\n\n"
                output += f"**Research Question**: {research_question}\n\n"
                output += f"### Hypothesis\n{design.get('hypothesis', 'N/A')}\n\n"
                output += f"### Methodology\n{design.get('methodology', 'N/A')}\n\n"
                output += f"### Sample Size\n{design.get('sample_size', 'N/A')}\n\n"
                output += f"### Controls\n{design.get('controls', 'N/A')}\n\n"
                output += f"### Statistical Tests\n{design.get('statistical_tests', 'N/A')}\n\n"
                output += f"### Potential Confounders\n{design.get('confounders', 'N/A')}\n\n"
                return output
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection error: {str(e)}"

async def analyze_image(image, analysis_type="disease_detection"):
    """Analyze a plant image."""
    try:
        import base64
        from io import BytesIO
        from PIL import Image
        
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE}/api/v1/image/analyze",
                json={
                    "image": img_base64,
                    "analysis_type": analysis_type
                }
            )
            if response.status_code == 200:
                data = response.json()
                results = data.get("analysis_results", {})
                output = f"## Image Analysis ({analysis_type})\n\n"
                output += f"**Confidence**: {results.get('confidence', 'N/A')}\n\n"
                output += f"**Results**: {results.get('results', 'N/A')}\n\n"
                output += f"**Recommendations**: {results.get('recommendations', 'N/A')}\n"
                return output
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection error: {str(e)}"

async def query_knowledge_graph(entity_name, entity_type="Gene"):
    """Query the knowledge graph."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{API_BASE}/api/v1/knowledge/query",
                json={"entity_name": entity_name, "entity_type": entity_type}
            )
            if response.status_code == 200:
                data = response.json()
                relationships = data.get("relationships", [])
                if not relationships:
                    return "No relationships found."
                output = f"## Knowledge Graph: {entity_name}\n\n"
                for rel in relationships:
                    output += f"- **{rel.get('source', 'N/A')}** → {rel.get('relationship', 'N/A')} → **{rel.get('target', 'N/A')}**\n"
                return output
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection error: {str(e)}"

with gr.Blocks(
    title="Plant Intelligence Platform - AI Research Assistant",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container { max-width: 1200px; margin: auto; }
    .header { text-align: center; padding: 20px; }
    """
) as app:
    gr.Markdown("""
    # 🌱 Plant Intelligence Platform
    ## AI-Powered Scientific Research Assistant
    
    Access the full power of PIP's AI agents for plant science research.
    """)
    
    with gr.Tabs():
        with gr.TabItem("💬 Research Chat"):
            gr.Markdown("### Chat with AI Research Assistant")
            gr.Markdown("Ask scientific questions about plant biology, genetics, and more.")
            chatbot = gr.ChatInterface(
                fn=research_chat,
                examples=[
                    "What are the key genes involved in drought tolerance in Arabidopsis?",
                    "Explain the role of ABA signaling in stomatal regulation",
                    "What statistical test should I use for comparing gene expression?",
                ],
                cache_examples=False
            )
        
        with gr.TabItem("📚 Literature Search"):
            gr.Markdown("### Search PubMed")
            with gr.Row():
                search_input = gr.Textbox(label="Search Query", placeholder="e.g., plant drought tolerance mechanisms")
                search_results = gr.Slider(minimum=1, maximum=20, value=5, step=1, label="Max Results")
            search_btn = gr.Button("Search", variant="primary")
            search_output = gr.Markdown(label="Results")
            search_btn.click(fn=search_literature, inputs=[search_input, search_results], outputs=search_output)
        
        with gr.TabItem("📝 Summarize Paper"):
            gr.Markdown("### Summarize Scientific Paper")
            paper_input = gr.Textbox(label="Paste Paper Abstract or Text", lines=10, placeholder="Paste paper text here...")
            summarize_btn = gr.Button("Summarize", variant="primary")
            summary_output = gr.Markdown(label="Summary")
            summarize_btn.click(fn=summarize_paper, inputs=paper_input, outputs=summary_output)
        
        with gr.TabItem("🧬 Gene Recommendations"):
            gr.Markdown("### Get Gene Recommendations")
            with gr.Row():
                phenotype_input = gr.Textbox(label="Phenotype", placeholder="e.g., drought tolerance")
                species_input = gr.Textbox(label="Species", value="Arabidopsis thaliana")
            gene_btn = gr.Button("Get Recommendations", variant="primary")
            gene_output = gr.Markdown(label="Recommendations")
            gene_btn.click(fn=get_gene_recommendations, inputs=[phenotype_input, species_input], outputs=gene_output)
        
        with gr.TabItem("🔬 Experiment Design"):
            gr.Markdown("### Design an Experiment")
            question_input = gr.Textbox(label="Research Question", placeholder="e.g., Does gene X affect drought tolerance?")
            variables_input = gr.Textbox(label="Variables (comma-separated)", placeholder="e.g., temperature, water stress")
            design_btn = gr.Button("Design Experiment", variant="primary")
            design_output = gr.Markdown(label="Experiment Design")
            design_btn.click(fn=design_experiment, inputs=[question_input, variables_input], outputs=design_output)
        
        with gr.TabItem("🖼️ Image Analysis"):
            gr.Markdown("### Analyze Plant Images")
            image_input = gr.Image(label="Upload Plant Image", type="pil")
            analysis_type = gr.Dropdown(
                choices=["disease_detection", "phenotype_measurement", "growth_analysis"],
                label="Analysis Type",
                value="disease_detection"
            )
            analyze_btn = gr.Button("Analyze", variant="primary")
            image_output = gr.Markdown(label="Analysis Results")
            analyze_btn.click(fn=analyze_image, inputs=[image_input, analysis_type], outputs=image_output)
        
        with gr.TabItem("🕸️ Knowledge Graph"):
            gr.Markdown("### Query Knowledge Graph")
            with gr.Row():
                entity_input = gr.Textbox(label="Entity Name", placeholder="e.g., DREB2A")
                entity_type = gr.Dropdown(
                    choices=["Gene", "Protein", "Pathway", "Phenotype", "Compound"],
                    label="Entity Type",
                    value="Gene"
                )
            kg_btn = gr.Button("Query", variant="primary")
            kg_output = gr.Markdown(label="Relationships")
            kg_btn.click(fn=query_knowledge_graph, inputs=[entity_input, entity_type], outputs=kg_output)
    
    gr.Markdown("""
    ---
    **Plant Intelligence Platform** | [GitHub](https://github.com/newdevelopment005/plant-intelligence-platform) | [Documentation](https://github.com/newdevelopment005/plant-intelligence-platform/blob/main/README.md)
    """)

if __name__ == "__main__":
    app.launch()
