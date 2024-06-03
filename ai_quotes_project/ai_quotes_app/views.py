from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from .serializers import QuoteSerializer,UploadedPDFSerializer
from .models import Quotes_DB
import openai
from PIL import Image
import os
import uuid
from pdf2image import convert_from_path
from django.conf import settings
import requests
import base64
from django.http import JsonResponse
from io import BytesIO

openai.api_key = "sk-proj-IomrCetlMNSg4Qu6FFFaT3BlbkFJk4MEgZFhi2lFIOQVsljt"
def baseurl(request):
  """
  Return a BASE_URL template context for the current request.
  """
  if request.is_secure():
    scheme = "https://"
  else:
    scheme = "http://"

  return scheme + request.get_host()


class FetchQuotesView(APIView):
    def get(self, request):
        api_key = 'UJnptKdZZ0xlkwpWJxup9w==bPgdsIvOB7Lwfd2h'  # Replace with your actual API Ninjas API key
        url = 'https://api.api-ninjas.com/v1/quotes'
        headers = {'X-Api-Key': api_key}

        # Fetch a random quote
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            quote_data = response.json()[0]
            quote = quote_data['quote']
            author = quote_data['author']

            # Summarize the quote using OpenAI
            prompt = f"Summarize the following quote in a way that a fifth grader can understand:\n\n'{quote}'\n\nAcknowledge the author."
            openai_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            summary = openai_response.choices[0].message['content'].strip()

            return Response({
                'quote': quote,
                'author': author,
                'summary': summary
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to fetch quote'}, status=response.status_code)


##### for pdf docfile uplaod
class PDFPagesAPIView(APIView):
    def post(self, request):
        serializer = UploadedPDFSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_pdf = serializer.save()
            pdf_path = uploaded_pdf.pdf_file.path
            images = convert_from_path(pdf_path)

            # Generate a unique directory name using UUID
            unique_dir_name = str(uuid.uuid4())
            base_dir = os.path.join(settings.MEDIA_ROOT, 'extracted_image')  # Construct the path relative to MEDIA_ROOT
            os.makedirs(base_dir, exist_ok=True)

            base_url = baseurl(request)  # Get the base URL for the current request
            image_urls = []
            for i, image in enumerate(images):
                image_name = f"page_{i + 1}.jpg"
                image_path = os.path.join('media', 'extracted_image', image_name)
                image.save(os.path.join(base_dir, image_name))
                final_path= f"{base_url}/{image_path}"
                image_urls.append(final_path)

            return Response({'image_urls': image_urls}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

## AI Agent start from here


def construct_payload(api_key, image_data_uri, prompt):

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt_messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": image_data_uri
                }
            ],
        },
    ]

    params = {
        "model": "gpt-4-vision-preview",
        "messages": prompt_messages,
        "max_tokens": 500,
    }

    return params, headers

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode("utf-8")
        return f"data:image/jpeg;base64,{base64_image}"


def send_message(payload, headers):

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")


# API Gather Information by AI Agent
class Generate_DescriptionAPIView(APIView):

    def post(self, request):
        api_key = "sk-proj-IomrCetlMNSg4Qu6FFFaT3BlbkFJk4MEgZFhi2lFIOQVsljt"
        data = request.data
        # Ensure data is a list
        if not isinstance(data, list):
            return Response({'error': 'Invalid input format. Expected a list of dictionaries.'},
                            status=status.HTTP_400_BAD_REQUEST)

        new_data = []
        try:
            for index, item in enumerate(data):
                print(index, item, "---------index index")
                image_urls = item.get('image_url', [])
                print(image_urls, "===============ooooooooooooo")
                print(f"Received image URLs: {image_urls}+++++++++++++++++mainlist from server")

                for i, image_url in enumerate(image_urls, start=1):
                    print(f"Processing Data URL: {image_url}")
                    print(i, "-----iiiiiii pprint")
                    # Construct the local image path with a specific name
                    local_image_path = os.path.join(settings.BASE_DIR, 'media/upload_image', f"image_{index}_{i}.jpg")
                    print(local_image_path, "--------bbbbbbbbbbbbbbb")
                    response = requests.get(image_url)
                    # Check if the request was successful
                    if response.status_code == 200:
                        # Open the image using PIL
                        image = Image.open(BytesIO(response.content))

                        if os.path.exists(local_image_path):
                            print("------exists____")
                            main_path = os.path.join(settings.BASE_DIR, 'media/upload_image')
                            print(main_path, "-----------------------main path")
                            for img_name in os.listdir(main_path):
                                print(img_name, "---image file name under main path")
                                print(os.path.join(main_path, img_name))
                                os.remove(os.path.join(main_path, img_name))
                            print(local_image_path, "--------local_image_path-- AFTER REMOVE ")
                        # Save the image to the local path
                        image.save(local_image_path)
                        print(f"Image saved at: {local_image_path}")
                    else:
                        print(f"Failed to download image from: {image_url}")

            base_path = os.path.join(settings.BASE_DIR, 'media/upload_image')
            prompt_template = f"""Your task is to analyze the given images. 
            And give me a full description about the given images.
            Important Note: Do not give descriptions out of context."""
            final_prompt = prompt_template
            print(final_prompt, "---------+++++++final_prompt")
            image_files = []
            for file in os.listdir(base_path):
                print(file, "image file taken from directory")
                if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
                    image_files.append(os.path.join(base_path, file))
            # print(image_files, "-------image list")
            for image_file in image_files:

                global image_data_uri
                image_data_uri = encode_image_to_base64(image_file)
                # print(image_data_uri, "----------++++++decode ")
                payload, headers = construct_payload(api_key, image_data_uri, final_prompt)
                # Send the message and get the response
                response = send_message(payload, headers)
                print(response, "--------response just after payload")
                print(type(response), "-------response type result after")

                # Check if response is not None before accessing its contents
                if response is not None and 'choices' in response and len(response['choices']) > 0 and 'message' in \
                        response['choices'][0] and 'content' in response['choices'][0]["message"]:
                    new_response = response['choices'][0]["message"]["content"]
                    # print(new_response, "-------++++++  new_response")
                    final_response = new_response.replace("\n", " ")

                    new_data.append(final_response)

                else:
                    print("Error processing response for image:", image_file)
            return Response({"data": new_data, 'status': status.HTTP_200_OK,"Message":"Successfully given information/description by AI agent"})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

