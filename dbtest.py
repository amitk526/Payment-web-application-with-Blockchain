from sqlalchemy import create_engine

db_uri = 'sqlite:///myBank.db' 
engine = create_engine(db_uri)

result1 = engine.execute('SELECT * FROM "user"')
#print(result.fetchall())

for r1 in result1:
   print(r1)

result2 = engine.execute('SELECT * FROM "profile"')
#print(result.fetchall())

for r2 in result2:
   print(r2)


result3 = engine.execute('SELECT * FROM "transactions"')
#print(result.fetchall())

for r3 in result3:
   print(r3)
