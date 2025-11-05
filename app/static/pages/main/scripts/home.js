const domController = () => {
    const _cache = {
        hour: document.querySelector(".hour"),
        minute: document.querySelector(".minute"),
    };

    const updateTime = () => {
        const now = new Date();
        const { hour, minute } = _cache;

        const hoursStr = String(now.getHours()).padStart(2, '0');
        const minutesStr = String(now.getMinutes()).padStart(2, '0');

        hour.textContent = hoursStr;
        minute.textContent = minutesStr;
    }

    updateTime()

    setInterval(updateTime, 1000)

    return {
        startInterval
    }
}

domController()