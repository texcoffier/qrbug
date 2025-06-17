function toggleQrSelection(element) {
    const className = 'qr_selected';
    const parentElement = element.parentElement.parentElement.parentElement;
    if (element.checked) {
        parentElement.classList.add(className);
    } else {
        parentElement.classList.remove(className);
    }
    return false;
}