fetch("/admin/interactions?limit=50")
    .then(res => res.json())
    .then(data => {
        const rows = data.map(item => `
            <tr>
                <td>${new Date(item.timestamp).toLocaleString()}</td>
                <td>${item.user_id}</td>
                <td>${item.query}</td>
                <td class="ai-${item.ai_provider}">${item.ai_provider}</td>
                <td>${item.response}</td>
            </tr>
        `);
        document.getElementById("ai-logs").innerHTML = rows.join("");
    });
    