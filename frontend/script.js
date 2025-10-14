// Sign in mock
function signIn() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  if (email && password) {
    alert("Login successful!");
    window.location.href = "map.html";
  } else {
    alert("Please fill in all fields.");
  }
}

// Google Map init
function initMap() {
  const farmLocation = { lat: 14.0778, lng: 121.3278 }; // Example: San Pablo, Laguna
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 12,
    center: farmLocation,
  });

  new google.maps.Marker({
    position: farmLocation,
    map: map,
    title: "Your Farm",
  });
}

// Mock prediction
function predictDisease() {
  const diseases = ["Rice Blast", "Bacterial Leaf Blight", "Sheath Blight", "Healthy"];
  const random = diseases[Math.floor(Math.random() * diseases.length)];
  document.getElementById("result").textContent = "Prediction: " + random;
}
