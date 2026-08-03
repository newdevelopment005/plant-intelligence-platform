import gradio as gr
import os
import sys
import importlib.util

# Add the app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after path setup
from app.agents.research_agent import ResearchAgent
from app.agents.literature_agent import LiteratureAgent
from app.agents.image_agent import ImageAnalysisAgent
from app.agents.knowledge_agent import KnowledgeGraphAgent
from app.config import Settings

settings = Settings()

# Initialize agents
research_agent = ResearchAgent(settings)
literature_agent = LiteratureAgent(settings)
image_agent = ImageAnalysisAgent(settings)
knowledge_agent = KnowledgeGraphAgent(settings)

async def research_chat(message, history):
    """Chat with the AI Research Assistant."""
    try:
        result = await research_agent.chat(message, session_id="gradio-user")
        return result.get("response", "No response")
    except Exception as e:
        return f"Error: {str(e)}"

async def search_literature(query, max_results=5):
    """Search PubMed for scientific papers."""
    try:
        result = await literature_agent.search(query, max_results=int(max_results))
        papers = result.get("results", [])
        if not papers:
            return "No papers found."
        output = f"## Found {len(papers)} papers\n\n"
        for i, paper in enumerate(papers, 1):
            output += f"### {i}. {paper.get('title', 'N/A')}\n"
            output += f"- **Authors**: {paper.get('authors', 'N/A')}\n"
            output += f"- **Journal**: {paper.get('journal', 'N/A')} ({paper.get('year', 'N/A')})\n"
            output += f"- **PMID**: {paper.get('pmid', 'N/A')}\n\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

async def summarize_paper(text):
    """Summarize a scientific paper."""
    try:
        result = await literature_agent.summarize(text)
        summary = result.get("summary", "No summary")
        findings = result.get("key_findings", [])
        output = f"## Summary\n\n{summary}\n\n"
        if findings:
            output += "## Key Findings\n\n"
            for f in findings:
                output += f"- {f}\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

async def get_gene_recommendations(phenotype, species):
    """Get gene recommendations."""
    try:
        result = await research_agent.recommend_genes(phenotype, species)
        genes = result.get("recommendations", [])
        if not genes:
            return "No recommendations found."
        output = f"## Gene Recommendations\n\n**Phenotype**: {phenotype}\n**Species**: {species}\n\n"
        for i, gene in enumerate(genes, 1):
            output += f"### {i}. {gene.get('gene_name', 'N/A')}\n"
            output += f"- **Function**: {gene.get('function', 'N/A')}\n"
            output += f"- **Evidence**: {gene.get('evidence', 'N/A')}\n"
            output += f"- **Confidence**: {gene.get('confidence', 'N/A')}\n\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

async def design_experiment(question, variables):
    """Design an experiment."""
    try:
        vars_list = [v.strip() for v in variables.split(",") if v.strip()] if variables else []
        result = await research_agent.design_experiment(question, vars_list)
        design = result.get("experiment_design", {})
        output = f"## Experiment Design\n\n"
        output += f"**Research Question**: {question}\n\n"
        output += f"### Hypothesis\n{design.get('hypothesis', 'N/A')}\n\n"
        output += f"### Methodology\n{design.get('methodology', 'N/A')}\n\n"
        output += f"### Sample Size\n{design.get('sample_size', 'N/A')}\n\n"
        output += f"### Controls\n{design.get('controls', 'N/A')}\n\n"
        output += f"### Statistical Tests\n{design.get('statistical_tests', 'N/A')}\n\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

async def analyze_image(image, analysis_type):
    """Analyze a plant image."""
    try:
        import base64
        from io import BytesIO
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        result = await image_agent.analyze(img_base64, analysis_type)
        results = result.get("analysis_results", {})
        output = f"## Image Analysis ({analysis_type})\n\n"
        output += f"**Confidence**: {results.get('confidence', 'N/A')}\n\n"
        output += f"**Results**: {results.get('results', 'N/A')}\n\n"
        output += f"**Recommendations**: {results.get('recommendations', 'N/A')}\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

async def query_knowledge_graph(entity_name, entity_type):
    """Query the knowledge graph."""
    try:
        result = await knowledge_agent.query(entity_name, entity_type)
        relationships = result.get("relationships", [])
        if not relationships:
            return "No relationships found."
        output = f"## Knowledge Graph: {entity_name}\n\n"
        for rel in relationships:
            output += f"- **{rel.get('source', 'N/A')}** → {rel.get('relationship', 'N/A')} → **{rel.get('target', 'N/A')}**\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

# Build Gradio UI
with gr.Blocks(
    title="Plant Intelligence Platform",
    theme=gr.themes.Soft()
) as app:
    gr.Markdown("""
    # 🌱 Plant Intelligence Platform
    ## AI-Powered Scientific Research Assistant
    """)
    
    with gr.Tabs():
        with gr.TabItem("💬 Research Chat"):
            gr.Markdown("### Chat with AI Research Assistant")
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
                search_input = gr.Textbox(label="Search Query", placeholder="plant drought tolerance")
                search_max = gr.Slider(minimum=1, maximum=20, value=5, step=1, label="Max Results")
            search_btn = gr.Button("Search", variant="primary")
            search_output = gr.Markdown(label="Results")
            search_btn.click(fn=search_literature, inputs=[search_input, search_max], outputs=search_output)
        
        with gr.TabItem("📝 Summarize Paper"):
            gr.Markdown("### Summarize Scientific Paper")
            paper_input = gr.Textbox(label="Paper Text", lines=10, placeholder="Paste paper abstract or text here...")
            summarize_btn = gr.Button("Summarize", variant="primary")
            summary_output = gr.Markdown(label="Summary")
            summarize_btn.click(fn=summarize_paper, inputs=paper_input, outputs=summary_output)
        
        with gr.TabItem("🧬 Gene Recommendations"):
            gr.Markdown("### Get Gene Recommendations")
            with gr.Row():
                phenotype_input = gr.Textbox(label="Phenotype", placeholder="drought tolerance")
                species_input = gr.Textbox(label="Species", value="Arabidopsis thaliana")
            gene_btn = gr.Button("Get Recommendations", variant="primary")
            gene_output = gr.Markdown(label="Recommendations")
            gene_btn.click(fn=get_gene_recommendations, inputs=[phenotype_input, species_input], outputs=gene_output)
        
        with gr.TabItem("🔬 Experiment Design"):
            gr.Markdown("### Design an Experiment")
            question_input = gr.Textbox(label="Research Question", placeholder="Does gene X affect drought tolerance?")
            variables_input = gr.Textbox(label="Variables (comma-separated)", placeholder="temperature, water stress")
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
                entity_input = gr.Textbox(label="Entity Name", placeholder="DREB2A")
                entity_type = gr.Dropdown(
                    choices=["Gene", "Protein", "Pathway", "Phenotype", "Compound"],
                    label="Entity Type",
                    value="Gene"
                )
            kg_btn = gr.Button("Query", variant="primary")
            kg_output = gr.Markdown(label="Relationships")
            kg_btn.click(fn=query_knowledge_graph, inputs=[entity_input, entity_type], outputs=kg_output)

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
