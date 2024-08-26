# learning about callbacks :)

def process_data(data, callback):
    # Simulate processing
    result = f"Processed {data}"
    callback(result)

def on_data_processed(result):
    print(f"Callback received: {result}")

# Using the callback
process_data("some data", on_data_processed)
