
from internetarchive import search_items,get_item



def search_in_archive(topic:str):
  q = f"{topic} AND collection:(journals) AND format:(Text PDF) AND mediatype:(texts)"
  arch_res = search_items(query=q)
  print(arch_res)
  res = []  
  for r in arch_res:
    Id = r['identifier']
    item = get_item(Id)
    print(item)
    title = item.item_metadata['metadata']['title']
    try:
      author = item.item_metadata['metadata']['creator']
    except KeyError:
      author = item.item_metadata['metadata']['uploader']
    try:
      year = item.item_metadata['metadata']['date']
    except KeyError:
      year = item.item_metadata['metadata']['publicdate']
    
    url = f"https://archive.org/details/{Id}"
    r = {'title':title,'authors':author,'pdf_url':url,'published':year}
    res.append(r)
    if len(res) > 4:
      break
  return res
res = search_in_archive('Artifical intelligence applications in cyber security')
print(res)
url = 'http://127.0.0.1:8000/literature/'
data = {
    "Researches":res,
    "style": "apa"
}
#r = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
#print(r.json())

    