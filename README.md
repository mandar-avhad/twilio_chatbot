# Chatbot for End Users to virtually Try-On different dresses


This project is a Twilio chatbot which uses FastAPI in backend to process the input image for Virtual Try-ON which is done using gradio huggingface space.

Techniques used:
- Twilio server for whatsapp chatbot 
- FastAPI
- Gradio Client
- Render (For hosting this FastAPI server)

Future Scope:
- Improving the chat interface to make it more user friendly.
- Handling the cache to delete older entries as soon as new entries over writes them



## Cloning the repo

```bash
git clone this_repo_url
```
this_repo_url: copy paste the repo of this url


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the requirements.
Note: If you do pip install, you will have to download the models, weights manually and place it in the respective folders.
```bash
!pip install -r requirements.txt
```

## Usage

```python
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
Run the above command to start the FastAPI server

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.
Suggestions are also welcome.
Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)