from bottle import route, run, request, response
import llm_extract_material_amount as llm


# We create the object used to interact with the llm
materials_amount_conversation_handler = llm.get_conversation_to_extract_material_amount(llm.init_llm())


@route('/materialApi')
def material_api():
    response.content_type = "application/json"

    # Fail if the mandatory arguments have not been passed (material, device)
    if "device" not in request.params:
        response.status = 501
        return 'No device given'

    # Ask the llm to estimate the content
    llm_response = llm.get_critical_raw_material_estimation(request.params['device'], materials_amount_conversation_handler)

    return llm_response


if __name__ == "__main__":
    run(host='0.0.0.0', port=8000)