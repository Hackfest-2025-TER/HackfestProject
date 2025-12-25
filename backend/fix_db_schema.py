
from sqlalchemy import create_engine, text
from database import DATABASE_URL

def fix_schema():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Fixing manifesto_votes table...")
        try:
            conn.execute(text("ALTER TABLE manifesto_votes ALTER COLUMN nullifier TYPE VARCHAR(128);"))
            print("✓ manifesto_votes.nullifier updated to VARCHAR(128)")
        except Exception as e:
            print(f"Error updating manifesto_votes: {e}")
            
        print("Fixing comment_votes table...")
        try:
            conn.execute(text("ALTER TABLE comment_votes ALTER COLUMN nullifier TYPE VARCHAR(128);"))
            print("✓ comment_votes.nullifier updated to VARCHAR(128)")
        except Exception as e:
            print(f"Error updating comment_votes: {e}")

        # Also checking comments session_id just in case
        print("Fixing comments table...")
        try:
            conn.execute(text("ALTER TABLE comments ALTER COLUMN session_id TYPE VARCHAR(128);"))
            print("✓ comments.session_id updated to VARCHAR(128)")
        except Exception as e:
            print(f"Error updating comments: {e}")
            
        conn.commit()
        print("Schema fix complete.")

if __name__ == "__main__":
    fix_schema()
