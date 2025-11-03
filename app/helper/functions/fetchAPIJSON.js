const postResponse = async (payload, url) => {
    const res = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CRSFToken": window.CSRF,
        },
        body: JSON.stringify(payload),
    });

    return res.json();
};

const getResponse = async (url) => {
    const res = await fetch(url, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "X-CRSFToken": window.CSRF,
        },
    });

    return res.json();
};

export default {
    postResponse,
    getResponse,
};