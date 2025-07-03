const testCases = {
    'active': 'L\'Incident est actif',
    'contains': (selector) => ` contient <i>${selector.value}</i>`,
    'true': ' est vrai',
    'false': ' est faux',
    'pending_feedback': ' en attente de retours',
    'is_for_thing': ' est pour l\'objet',
    'is_for_user': ' est pour l\'utilisateur',
    'in': (selector) => {
        if (selector?.class === 'User' || selector?.class === 'Failure') {
            return ` est dans le groupe <i>${selector.value}</i>`;
        } else {
            return ` est dans <i>${selector.value}</i>`;
        }
    },
    'in_or_equal': (selector) => ` est dans/est <i>${selector.value}</i>`,
    'is': (selector) => ` est <i>${selector.value}</i>`,
    'True': ' est True',
    'default': (selector, value) => {
        if (['<','>','<=','>=','='].includes(value)) {
            return ` ${value} <i>${selector.value}</i>`;
        } else {
            throw new Error("Test selector not known");
        }
    }
}

const classCases = {
    'Incident': `l\'Incident`,
    'Thing': `l\'Objet`,
    'Failure': `la Panne`,
    'User': `l\'Utilisateur`,
    'Selector': (selector) => `le Sélecteur d'ID "${selector.id}"`,
    'SourceThing': `l\'Objet Source`,
    'SourceFailure': `la Panne Source`,
    'SourceUser': `l\'Utilisateur Source`,
    'default': () => {
        throw new Error("Class selector not known");
    }
}

const operators = ["OU", "ET"];

function handleTestCases(testCases, value, selector) {
    let sentence = '';
    let correctTestCase = testCases[value];
    if (correctTestCase === undefined) {
        correctTestCase = testCases["default"];
    }
    if (typeof correctTestCase === 'function') {
        sentence += correctTestCase(selector, value);
    } else if (typeof correctTestCase === 'string') {
        sentence += correctTestCase;
    } else {
        throw new Error("What-");
    }
    return sentence;
}

function transcribeSelector(selector) {
    let sentence = '';
    if (Array.isArray(selector)) {
        sentence = '(' + transcribeSelector(selector[1]) + ')' + ` <b>${operators[selector[0]]}</b> ` + '(' + transcribeSelector(selector[2]) + ')';
    } else {
        for (const [key, value] of Object.entries(selector)) {
            if (key === 'test') {
                sentence += handleTestCases(testCases, value, selector);
            }
            else if (key === 'class') {
                sentence += handleTestCases(classCases, value, selector);
            }
            else if (key === 'attr') {
                sentence += ` <i>(attribut "${value}")</i>`;
            }
        }
    }
    sentence = sentence.replaceAll(/^ +/g, '');
    if (sentence !== '') {
        return sentence[0].toUpperCase() + sentence.slice(1);
    } else {
        return sentence;
    }
}

function updateRenderedSelector(selectorRepresentation) {
    document.getElementById('rendered_selector').innerHTML = transcribeSelector(JSON.parse(selectorRepresentation));
}

function sideToEditIndex() {
    return parseInt(document.querySelector('.selector_builder .side_selector select').value);
}

function addCondition(condition_type) {
    const rawSelector = document.getElementById('raw_selector');
    const rawSelectorValue = rawSelector.textContent;
    let selectorRepresentation = JSON.parse(rawSelectorValue);
    if (Array.isArray(selectorRepresentation)) {
        selectorRepresentation[0] = condition_type;
    } else {
        selectorRepresentation = [condition_type, selectorRepresentation, {}];
    }
    const stringifiedSelector = JSON.stringify(selectorRepresentation);
    rawSelector.textContent = stringifiedSelector;
    document.getElementById('input').setAttribute('value', stringifiedSelector);
    document.querySelector('.selector_builder .side_selector').style.display = (Array.isArray(selectorRepresentation)) ? 'block' : 'none';
    return stringifiedSelector;
}