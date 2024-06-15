import Swal from "sweetalert2";

export async function showAIResponse(response) {
    const parsedResponse = await response.json()
    console.log(parsedResponse)
    if (parsedResponse.error) {
        await Swal.fire('Error', parsedResponse.error, 'error')
    } else if (parsedResponse.parsed_answer) {
        await Swal.fire('Answer', parsedResponse.parsed_answer, 'info')
    } else if (parsedResponse.answer) {
        await Swal.fire('Answer', parsedResponse.answer, 'info')
    } else {
        await Swal.fire('Answer', JSON.stringify(parsedResponse), 'info')
    }
}