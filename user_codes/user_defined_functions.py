import time
import os

# Retry function with retries
def run_code_with_retries(retry_function, max_retries=5, retry_delay=1):
    retries = 0
    while retries < max_retries:
        try:
            return retry_function()  # Execute the function
        except Exception as e:  # Catch general exceptions
            print(f"Error occurred: {e}")
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retries += 1
    return f"Maximum retries ({max_retries}) reached."

# Execute generated code
def execute_code(code: str, data):
    try:
      local_namespace = {"df": data}
      exec(code, {}, local_namespace)
      return local_namespace.get("context_result")    
    except Exception as e:
        return f"Error in code execution: {e}"

# Delete existing image if any
def delete_image_if_exists(img_path):
    """
    Deletes the image file at the specified path if it exists.
    """
    if os.path.exists(img_path):
        os.remove(img_path)
        print(f"Image at '{img_path}' has been deleted.")
    else:
        print(f"No image found at '{img_path}' to delete.")

def check_image_if_exists(img_path):
    if os.path.exists(img_path):
        return True
    else:
        return False
