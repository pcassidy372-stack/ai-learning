# --- R: Read an existing file ---
with open("sample_data.txt", "r") as f:
    content = f.read()
print("READ:")
print(content)

# --- W: Write to a new file ---
with open("test_output.txt", "w") as f:
    f.write("This is a new write.\n")
    f.write("It will overwrite anything that was here before.\n")
print("WRITE: saved to test_output.txt")

# --- A: Append (adds to end, keeps existing content) ---
with open("test_output.txt", "a") as f:
    f.write("This line was appended.\n")
    f.write("The original content is still above this.\n")
print("APPEND: added two lines to test_output.txt")

# --- Prove W vs A difference ---
with open("test_output.txt", "r") as f:
    final = f.read()
print("\nFINAL FILE CONTENTS:")
print(final)