from bottle import app, route, run, request, response, BaseRequest
import llm_extract_material_amount as llm_api
import device_detector as detector
from bottle_cors_plugin import cors_plugin
import json

# We allow every kind of CORS
app = app()
app.install(cors_plugin('*'))

# We increase the maximum size of the request to allow the api to handle big images
BaseRequest.MEMFILE_MAX = 1024 * 1024

# We create the object used to interact with the llm
llm_obj = llm_api.init_llm()
print("Done")

# Return the estimation of crm contained into the device passed as an argument
@route('/materialApi')
def material_api():
    response.content_type = "application/json"

    # Fail if the mandatory arguments have not been passed (material, device)
    if "device" not in request.params:
        response.status = 501
        return 'No device given'

    # Ask the llm to estimate the content
    llm_response = llm_api.generate_api_info(request.params['device'], llm_obj)

    return llm_response


# Accepts an image as a parameter, detect the device in it and estimate the amount of crm
@route('/detectorApi', method='POST')
def material_api():
    response.content_type = "application/json"

    # Get the image from the request
    image = json.loads(request.body.read())['image']

    # Fail if the mandatory arguments have not been passed (base64 image)
    if image is None or image == "":
        response.status = 501
        return 'No image given'

    device = detector.detect_device(image)

    # Ask the llm to estimate the content
    # request.get("http://ec2-15-160-182-105.eu-south-1.compute.amazonaws.com:8080/api/getDeviceInfo?name=IphoneX")
    # TODO the request should be redirected directed to the main api
    llm_response = llm_api.generate_api_info(device, llm_obj)

    return llm_response


if __name__ == "__main__":
    run(host='0.0.0.0', port=8000)