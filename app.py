import streamlit as st
from langchain import PromptTemplate
from langchain.llms import Clarifai
import urllib.parse
from urllib.parse import quote

st.set_page_config(page_title="Generate your Email!!",page_icon=":📬:",layout="wide")

def main():
    # Create a two-column layout
    col1, col2 = st.columns(2)
    with col1:

        st.title("Email Generator")
        
        
        
        # User input for sender's name
        sender_name = col1.text_input("Sender's Name", key="sender_name", value="")
        
        # User input for recipient's name
        recipient_name = col1.text_input("Recipient's Name", key="recipient_name", value="")
        
        # User input for email subject/topic
        subject = col1.text_input("Subject/Topic", key="subject", value="")
        
        # User input for extra detail (optional)
        extra_detail = col1.text_input("Extra Detail", key="extra_detail", value="")

        # User input for email tone with dropdown
        tone_options = ['Formal', 'Casual', 'Friendly']
        tone = col1.selectbox("Tone", tone_options, key="tone", index=0)
        
        # User input for preferred email length
        length_options = ['Short', 'Medium', 'Long']
        preferred_length = col1.selectbox("Preferred Length", length_options, key="preferred_length", index=0)
        
        # User input for attachments
        attachments = col1.file_uploader("Attachments", type=["pdf", "txt", "docx"], accept_multiple_files=True, key="attachments")
    
    with col2:
        col2.title("Email Preview")

    with col1:
        # Create Email button
        if col1.button("Create Email"):
            if sender_name and recipient_name and subject and tone and preferred_length:
                email_content = generate_email(sender_name, recipient_name, subject, extra_detail, tone, preferred_length, attachments)
                with col2:
                    with st.expander("Preview Box", expanded=True):
                        st.write(email_content)
                        if email_content:
                            email_links = generate_email_links(recipient_name, subject, email_content)
                            mail_link, gmail_link=email_links
                            st.markdown(f"[Open with Email Client]({mail_link})")
                            st.markdown(f"[Open with Gmail]({gmail_link})")
            else:
                st.warning("Please fill in all required fields.")
                
def generate_email_links(recipient_name, subject, email_content):
    encoded_subject = urllib.parse.quote(subject)
    encoded_body = urllib.parse.quote(email_content)

    mail_link = f"mailto:{recipient_name}?subject={encoded_subject}&body={encoded_body}"

    gmail_link = f"https://mail.google.com/mail/?view=cm&su={encoded_subject}&body={encoded_body}"


    return mail_link,gmail_link




# function to generate email
def generate_email(sender_name, recipient_name, subject, extra_detail, tone, preferred_length, attachments):

    
    ######################################################################################################
    # In this section, we set the user authentication, user and app ID, model details, and the URL of 
    # the text we want as an input. Change these strings to run your own example.
    ######################################################################################################

    # Your PAT (Personal Access Token) can be found in the portal under Authentification
    PAT = '30cbbd7e47ba49c7a013f03c44f2b289'
    # Specify the correct user_id/app_id pairings
    # Since you're making inferences outside your app's scope
    USER_ID = 'meta'
    APP_ID = 'Llama-2'
    # Change these to whatever model and text URL you want to use
    MODEL_ID = 'llama2-13b-chat'
    MODEL_VERSION_ID = '79a1af31aa8249a99602fc05687e8f40'
    TEXT_FILE_URL = 'https://samples.clarifai.com/negative_sentence_12.txt'

    ############################################################################
    # YOU DO NOT NEED TO CHANGE ANYTHING BELOW THIS LINE TO RUN THIS EXAMPLE
    ############################################################################

    from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
    from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
    from clarifai_grpc.grpc.api.status import status_code_pb2

    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    metadata = (('authorization', 'Key ' + PAT),)

    userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

    post_model_outputs_response = stub.PostModelOutputs(
        service_pb2.PostModelOutputsRequest(
            user_app_id=userDataObject,  # The userDataObject is created in the overview and is required when using a PAT
            model_id=MODEL_ID,
            version_id=MODEL_VERSION_ID,  # This is optional. Defaults to the latest model version
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        text=resources_pb2.Text(
                            url=TEXT_FILE_URL
                        )
                    )
                )
            ]
        ),
        metadata=metadata
    )
    if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
        print(post_model_outputs_response.status)
        raise Exception(f"Post model outputs failed, status: {post_model_outputs_response.status.description}")

    # Since we have one input, one output will exist here
    output = post_model_outputs_response.outputs[0]

    print("Completion:\n")
    print(output.data.text.raw)


    # template for building the prompt
    template = """Generate an email from {sender_name} to {recipient_name} with the following details:\nSubject: {subject}\n. Write it in a {tone} way. Make it {preferred_length} length and add details: {extra_detail}. 
    Write it in a proper format of a letter. Just write the email as if you are the one sending it. Make sure there are no repeated sentences. """
 
    if attachments:
        attachment_names = ", ".join([attachment.name for attachment in attachments])
        attachment_list = "\nAttachments: " + attachment_names  # Include a new line at the beginning
        template += attachment_list


    # creating the final prompt
    prompt=PromptTemplate(
        input_variables=["sender_name","recipient_name","subject","tone","preferred_length","extra_detail"],
        template=template,)
    
    llm=Clarifai(pat='e620301e1ebe4aa5ba634bcc668f8274',user_id='meta',app_id='Llama-2',model_id='llama2-13b-chat')

    # generating response using LLM
    response=llm(prompt.format(subject=subject,sender_name=sender_name,recipient_name=recipient_name,tone=tone,preferred_length=preferred_length,extra_detail=extra_detail))
    print(response)


    return response
    
    # return email_template

if __name__ == "__main__":
    main()
