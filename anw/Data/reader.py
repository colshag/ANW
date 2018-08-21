import csv

reader = csv.reader(open('regimentdata.csv', 'rb'))
for row in reader:
  print row