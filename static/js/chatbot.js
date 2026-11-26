// Đóng và mở Chatbox
function toggleChat() {
    const box = document.getElementById("chat-box");

    box.style.display =
        box.style.display === "block" ? "none" : "block";
}

// Hiển thị tin nhắn
function addMessage(message, className) {
    const messages = document.getElementById("chat-messages");
    const div = document.createElement("div");

    div.className = className;
    div.textContent = message;

    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

// Gửi tin nhắn
function sendMessage() {
    const input = document.getElementById("chat-input");
    const message = input.value.trim();

    if (message === "") return;

    addMessage(message, "user-message");

    input.value = "";

    const reply = getBotReply(message.toLowerCase());

    setTimeout(function () {
        addMessage(reply, "bot-message");
    }, 500);
}

// Chatbot tự động trả lời theo từ khóa
function getBotReply(message) {

    if (message.includes("xin chào") ||
        message.includes("hello") ||
        message.includes("hi")) {
        return "Xin chào! Chào mừng bạn đến với WatchStore. Tôi có thể giúp gì cho bạn?";
    }

    if (message.includes("đồng hồ nam")) {
        return "Bạn có thể tham khảo các mẫu đồng hồ nam trong danh sách sản phẩm của WatchStore.";
    }

    if (message.includes("đồng hồ nữ")) {
        return "Bạn có thể tham khảo các mẫu đồng hồ nữ thanh lịch tại cửa hàng.";
    }

    if (message.includes("casio")) {
        return "Casio là thương hiệu đồng hồ nổi tiếng của Nhật Bản, có nhiều mẫu mã và độ bền cao.";
    }

    if (message.includes("citizen")) {
        return "Citizen nổi tiếng với công nghệ Eco-Drive sử dụng năng lượng ánh sáng.";
    }

    if (message.includes("orient")) {
        return "Orient nổi tiếng với các dòng đồng hồ cơ có thiết kế sang trọng.";
    }

    if (message.includes("giá")) {
        return "Bạn có thể xem giá bán cụ thể tại danh sách sản phẩm trên website.";
    }

    if (message.includes("bảo hành")) {
        return "Vui lòng liên hệ cửa hàng để biết chính sách bảo hành của từng sản phẩm.";
    }

    if (message.includes("giao hàng") ||
        message.includes("vận chuyển")) {
        return "Vui lòng liên hệ cửa hàng để biết thời gian và chi phí giao hàng.";
    }

    if (message.includes("thanh toán")) {
        return "Bạn có thể xem phương thức thanh toán tại trang đặt hàng.";
    }

    if (message.includes("mua hàng") ||
        message.includes("đặt hàng")) {
        return "Bạn hãy chọn sản phẩm yêu thích, thêm vào giỏ hàng và tiến hành đặt hàng.";
    }

    if (message.includes("đăng ký")) {
        return "Bạn hãy chọn mục Đăng ký trên website để tạo tài khoản mới.";
    }

    if (message.includes("đăng nhập")) {
        return "Bạn hãy chọn mục Đăng nhập và nhập tên tài khoản, mật khẩu.";
    }

    if (message.includes("cảm ơn")) {
        return "Cảm ơn bạn đã quan tâm đến WatchStore. Chúc bạn một ngày tốt lành!";
    }

    return "Xin lỗi, tôi chưa hiểu câu hỏi của bạn. Bạn có thể hỏi về đồng hồ, giá bán, bảo hành hoặc cách đặt hàng.";
}

// Nhấn Enter để gửi tin nhắn
document.getElementById("chat-input")
    .addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });
