import os

import click
import requests
from openai import OpenAI

BASE_URL = "https://albert.api.etalab.gouv.fr/v1"
MODEL = "mistralai/Pixtral-12B-2409"
EMBEDDINGS_MODEL = "BAAI/bge-m3"


def get_client(api_key, base_url=BASE_URL):
    # OpenAI client configuration
    client = OpenAI(base_url=base_url, api_key=api_key)

    return client


def post_collection(
    session, collection_name, embeddings_model=EMBEDDINGS_MODEL, base_url=BASE_URL
):
    response = session.post(
        f"{base_url}/collections",
        json={"name": collection_name, "model": embeddings_model},
    )
    response = response.json()
    collection_id = response["id"]
    return collection_id


def post_files(
    file_paths,
    session,
    collection_id,
    base_url=BASE_URL,
):
    for f in file_paths:
        files = {
            "file": (
                os.path.basename(f),
                open(f, "rb"),
                "application/pdf",
            )
        }
        data = {"request": '{"collection": "%s"}' % collection_id}
        response = session.post(f"{base_url}/files", data=data, files=files)
        assert response.status_code == 201


def get_uploaded_files_number(session, collection_id, base_url=BASE_URL):
    response = session.get(f"{base_url}/documents/{collection_id}")
    assert response.status_code == 200
    files = response.json()["data"]
    return len(files)


def ask_llm(
    session, collection_id, adresse, client, language_model=MODEL, base_url=BASE_URL
):
    prompt = f"Que manque t il à la description du projet situé à l'adresse {adresse} pour correspondre aux préconisations du plan local d'urbanisme ? Précise les notions du PLU que tu utilises pour étayer ta réponse"
    data = {
        "collections": [collection_id],
        "k": 6,
        "prompt": prompt,
        "method": "semantic",
    }
    response = session.post(url=f"{base_url}/search", json=data)

    prompt_template = "Réponds à la question suivante en te basant sur les documents ci-dessous : {prompt}\n\nDocuments :\n\n{chunks}"
    chunks = "\n\n\n".join(
        [result["chunk"]["content"] for result in response.json()["data"]]
    )

    prompt = prompt_template.format(prompt=prompt, chunks=chunks)

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=language_model,
        stream=False,
        n=1,
    )

    response = response.choices[0].message.content
    print(response)


@click.command()
@click.option(
    "--files",
    "-f",
    default=[],
    multiple=True,
    type=click.Path(),
    help="Files to use as context.",
)
@click.option(
    "--api_key",
    required=True,
    type=str,
    help="api key.",
)
def main(files, api_key):
    client = get_client(api_key)

    session = requests.session()
    session.headers = {"Authorization": f"Bearer {api_key}"}

    collection_id = post_collection(session, collection_name="tutorial")

    post_files(file_paths=files, session=session, collection_id=collection_id)
    ask_llm(session=session, collection_id=collection_id, adresse="", client=client)


if __name__ == "__main__":
    main()
