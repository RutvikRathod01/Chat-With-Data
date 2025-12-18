import os
import gradio as gr

from dotenv import load_dotenv
from utils import proceed_input, process_user_question

# Load environment variables
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Create a directory to store Excels
os.makedirs('../data', exist_ok=True)


# Gradio app to process PDF and ask questions
def gradio_app():
    with gr.Blocks() as interface:
        with gr.Row():
            gr.Markdown("## Chat with Text, Docs, Excel and PDF ##")

        with gr.Row():
            text_input = gr.Textbox(label="Enter Text Paragraph", lines=10)
            file_upload = gr.File(label="Upload Doc,Excel or PDF Files", file_types=[".xlsx", ".pdf", ".docx"], file_count="multiple")

        with gr.Row():
            process_btn = gr.Button("Process")

        with gr.Row():
            output_message = gr.Textbox(label="Status")

        # State to persist across Gradio app runs (initialized to None)
        rag_chain_state = gr.State(None)

        # Chatbot interface
        chatbot = gr.Chatbot(
            elem_id="chatbot", bubble_full_width=False, scale=1)
        chat_input = gr.Textbox(
            placeholder="Ask a question about the Input...", show_label=False)

        def add_message(history, message):
            # Add user message to chat history
            if message is not None:
                history.append([message, None])
            return history, gr.Textbox(value=None, interactive=False)

        def process_input_gradio(text, files):
            # Update state with processed input data
            rag_chain = proceed_input(text, files)
            return "Data processed. Now you can ask questions.", rag_chain, None

        def ask_question_gradio(user_input, rag_chain_state):
            # Use the state to process the question
            rag_chain = rag_chain_state
            if rag_chain is None:
                return "Please upload and process input first."
            return process_user_question(user_input, rag_chain)

        def bot(history, rag_chain_state):
            # Get the bot's response and update the chat history
            history[-1][1] = ask_question_gradio(
                history[-1][0], rag_chain_state)
            return history

        # Connect processing button to the input processing function
        process_btn.click(fn=process_input_gradio, inputs=[text_input, file_upload], outputs=[
            output_message, rag_chain_state, chatbot])

        # Clear the chat history and input
        gr.ClearButton([chat_input, chatbot])

        # Ask a question and get the bot's response
        chat_msg = chat_input.submit(
            add_message, [chatbot, chat_input], [chatbot, chat_input])
        bot_msg = chat_msg.then(bot, [chatbot, rag_chain_state], chatbot)
        bot_msg.then(lambda: gr.Textbox(interactive=True), None, [chat_input])

    interface.launch(server_name="0.0.0.0", server_port=7000)


# Run the Gradio app
if __name__ == "__main__":
    # Launch Gradio app with server name and port
    gradio_app()
