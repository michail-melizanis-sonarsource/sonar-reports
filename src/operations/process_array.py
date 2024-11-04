from parser import parse_field
def execute(input_array, output_format, **kwargs):
    output_array = list()
    for i in input_array:
        inputs = dict(obj=i)
        output = dict()
        for k,v in output_format.items():
            output[k] = parse_field(obj=inputs, field_config=v)
        output_array.append(output)
    return output_array