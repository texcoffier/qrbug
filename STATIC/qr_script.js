function toggleQrSelection(checked, name) {
    const className = `qr_no_display_${name}`;
    if (!checked) {
        document.body.classList.add(className);
    } else {
        document.body.classList.remove(className);
    }
    return false;
}