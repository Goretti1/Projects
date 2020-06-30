import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for id, isbn, title, author, year in reader:
        db.execute("INSERT INTO books (id, isbn, title, author, year) VALUES (:id, :isbn, :title, :author, :year)",
                    {"id": id, "isbn": isbn, "title": title, "author": author, "year": year})
        print(f"ISBN: {isbn}, Book Title: {title}, Author: {author}, Year of Publication: {year}")
    db.commit()

if __name__ == "__main__":
    main()
