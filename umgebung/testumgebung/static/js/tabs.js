function switchTab(Tab) {
  // Declare all variables
  var i, tabcontent, tablinks;

  // Get all elements with class="tabcontent" and hide them
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("tablinks");
  for (const tablink of tablinks) {
    tablink.className = tablink.className.replace(" active", "");
  }
  // Show the current tab, and add an "active" class to the button that opened the tab
  const tabBody = document.getElementById(Tab)
  if (tabBody) {
    tabBody.style.display = "block";
    const tabElement = document.getElementById(`${Tab.toLowerCase()}-tab`)
    tabElement.className += " active";
    window.history.pushState('page', 'Title', `/admin?tab=${Tab.toLowerCase()}`);
  }
}
const urlParams = new URLSearchParams(window.location.search);
const tab = urlParams.get("tab")
switch (tab) {
  case "account":
    switchTab("Account")
    break;
  case "campus":
    switchTab("Campus")
    break;
  case "subjects":
    switchTab("Subjects")
    break;
  case "data":
    switchTab("Data")
    break;
  default:
    switchTab("Data")
}

