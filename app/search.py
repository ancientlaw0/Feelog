from flask import current_app

# Indexes a SQLAlchemy model into Elasticsearch
def add_to_index(index, model):
    if not current_app.elasticsearch:
        return  # If Elasticsearch isn't set up, silently skip indexing.
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, document=payload)


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0   # Fail gracefully if ES isn't available.
    search = current_app.elasticsearch.search(
        index=index,
        query={'multi_match': {'query': query, 'fields': ['*']}},
        from_=(page - 1) * per_page,
        size=per_page)
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']    # Return IDs and total hit count for pagination.
