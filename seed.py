# seed.py
from shared.models.database import engine, SessionLocal
from shared.models.models import Base, ActivitySpec

def init_db():
    """
    Initializes the database schema and seeds it with default activity specifications.
    """
    print("⏳ Creating tables in PostgreSQL...")
    # Base.metadata.create_all reads our SQLAlchemy models and automatically 
    # executes 'CREATE TABLE IF NOT EXISTS' SQL statements in our database.
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")

    # Create a fresh database transaction session
    db = SessionLocal()
    
    try:
        print("🌱 Seeding default activity specifications...")
        
        # Define our initial set of default activities
        default_activities = [
            ActivitySpec(
                activity_name="run",
                prep_duration=30,
                activity_duration=45,
                post_duration=45,
                alarm_on_prep=True,
                prep_description="Wake up and prepare for your morning run.",
                post_description="Shower and cool down after your run."
            ),
            ActivitySpec(
                activity_name="breakfast",
                prep_duration=30,
                activity_duration=30,
                post_duration=0,
                alarm_on_prep=True,
                prep_description="Start cooking. Prep details: {details}",
                post_description="Enjoy your meal!"
            )
        ]

        # Insert or update each activity in our database table
        for spec in default_activities:
            # Check if the activity configuration already exists in the database
            existing_spec = db.query(ActivitySpec).filter(
                ActivitySpec.activity_name == spec.activity_name
            ).first()
            
            if not existing_spec:
                db.add(spec)
                print(f"   [+] Seeded: {spec.activity_name}")
            else:
                print(f"   [-] Already exists: {spec.activity_name}")
                
        # Commit the transaction to save changes to the database safely
        db.commit()
        print("🎉 Database seeding completed successfully!")
        
    except Exception as e:
        db.rollback()  # Rollback any pending operations if something goes wrong
        print(f"❌ Error seeding database: {str(e)}")
    finally:
        db.close()     # Always close the database session to release connections

if __name__ == "__main__":
    init_db()
