const acquiredList = document.getElementsByClassName("list-items")[0]
const distractorList = document.getElementsByClassName("list-items")[1]
const missingList = document.getElementsByClassName("list-items")[2]

let next_entry = -1

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

function update(data) {
    // Convert data objects into lists
    acquired = []
    distractors = []
    missing = []

    console.log(data)

    data["state"]["missing"].forEach((name) => {
        missing.push(`${name} | 0`)
    })

    for(const [name, info] of Object.entries(data["state"]["acquired"])) {
        value = `${name} | ${info["confidence_score"]}`
        if(info["valid"]) {
            acquired.push(value)
        } else {
            missing.push(value)
        }
    }

    for(const [name, info] of Object.entries(data["state"]["distractors"])) {
        if(info["valid"]) {
            distractors.push(`${name} | ${info["confidence_score"].toFixed(2)}`)
        }
    }

    // Update page
    updateList(acquiredList, acquired);
    updateList(distractorList, distractors);
    updateList(missingList, missing);
}

function getData() {
    fetch(`/data/${next_entry}`)
    .then(response => {
        return response.json();
    }).then(state => {
        console.log(state)
        if("entry_num" in state) {
            next_entry = state["entry_num"] + 1;
            update(state);
        }
    });
}

setInterval(getData, 1000/15.0)