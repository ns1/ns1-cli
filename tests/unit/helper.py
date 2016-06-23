

def create_example_data_helper(example_filename):
    """A function to generate example data helpers."""
    directory = os.path.dirname(__file__)
    directory = os.path.join(directory, "json")
    example = os.path.join(directory, example_filename)

    def data_helper():
        with open(example) as fd:
            data = json.load(fd)
        return data

    return data_helper
