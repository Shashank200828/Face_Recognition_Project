import os

def remove_user_faces(user_id, folder='data/faces'):
    count = 0
    for fname in os.listdir(folder):
        parts = fname.split('.')
        if len(parts) == 4 and parts[1].isdigit() and int(parts[1]) == user_id:
            os.remove(os.path.join(folder, fname))
            count += 1
    print(f"Removed {count} images for UserID {user_id}")

if __name__ == "__main__":
    user_id = int(input("Enter the UserID to remove: "))
    remove_user_faces(user_id)