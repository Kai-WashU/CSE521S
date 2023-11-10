const acquiredList = document.getElementsByClassName("list-items")[0]
const distractorList = document.getElementsByClassName("list-items")[1]
const missingList = document.getElementsByClassName("list-items")[2]

let next_entry = 0

function updateList(listElement, values) {
    values.forEach((element, index) => {
        // If there is an un-updated entry element, update it
        if(index < listElement.children.length) {
            let entry = listElement.children[index];
            entry.innerHTML = element;
        } else {
            // If we are out of elements, create a new one
            let entry = document.createElement("li");
            entry.innerHTML = element;
            listElement.appendChild(entry);
        }
    })

    // Remove any elements that are no longer being used
    for(let index = values.length; index < listElement.children.length; index++) {
        listElement.children[index].remove();
    }
}

// TODO: Change to fit new data format
function update(data) {
    updateList(acquiredList, data["state"]["acquired"]);
    updateList(distractorList, data["state"]["distractors"]);
    updateList(missingList, data["state"]["missing"]);
}

function getData() {
    fetch(`/data/${next_entry}`)
    .then(response => {
        return response.json();
    }).then(state => {
        if("entry_num" in state) {
            next_entry = state["entry_num"] + 1;
            update(state["data"]);
        }
    });
}

//setInterval(getData, 1000 / 15.0)