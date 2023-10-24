import requests

claim = "Jackie (2016 film) was directed by Peter Jackson."
evidence = "Jackie is a 2016 biographical drama film directed by Pablo Larraín and written by Noah Oppenheim ."
web = requests.get(f"http://140.115.54.36/?claim={claim}&evidence={evidence}")
 
print(web.text)