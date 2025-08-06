import streamlit as st
from langchain.chains.question_answering import load_qa_chain
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders.unstructured import UnstructuredFileLoader

# Page configuration
st.set_page_config(page_title="Chatbot", layout="centered")
st.markdown("<h1 style='text-align: center;'>📘 Spintly Chatbot</h1>", unsafe_allow_html=True)
st.markdown("Ask a question based on the uploaded manual. Image content will be considered too!")

# File upload
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    # Save uploaded file temporarily
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    try:
        # Use Unstructured loader (handles text + image content)
        loader = UnstructuredFileLoader("temp.pdf")
        documents = loader.load()

        # Text splitting
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)

        # Embedding and vector store
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(docs, embeddings)

        st.success("✅ PDF processed (text + images)! Ask your question.")

        # Ask question
        query = st.text_input("🔍 Enter your question:")
        if query:
            try:
                # Use TinyLLaMA via Ollama
                llm = OllamaLLM(model="tinyllama", base_url="http://localhost:11434")
                chain = load_qa_chain(llm, chain_type="stuff")
                matching_docs = vectorstore.similarity_search(query)

                # Filter out short link-only chunks
                filtered_docs = [
                    doc for doc in matching_docs
                    if "http" not in doc.page_content.strip() or len(doc.page_content.strip()) > 100
                ]

                # Prompt to instruct summarization instead of just linking
                prompt = f"""Answer the following question using the content from the documents.
If any document contains a link, summarize the content of that link instead of providing the URL.

Question: {query}
"""

                response = chain.run(input_documents=filtered_docs, question=prompt)

                st.markdown("### 🤖 Answer:")
                st.write(response)

            except Exception as e:
                st.error(f"⚠️ Error generating response: {e}")

    except Exception as e:
        st.error(f"❌ Failed to load PDF: {e}")