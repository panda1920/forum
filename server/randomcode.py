import urllib.parse
from pathlib import Path

formData = urllib.parse.urlencode({
	'author': 'someone',
	'message': 'Hello world'
})

print(formData)

saveLocation = Path(__file__).resolve().parents[0] / 'temp'
fileName = saveLocation / 'temp.txt'

print(saveLocation)
print(fileName)