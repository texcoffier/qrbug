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
    'SourceThingUser': `l\'Utilisateur de l\'Objet Source`,
    'SourceFailure': `la Panne Source`,
    'SourceUser': `l\'Utilisateur Source`,
    'FilterThing': `l\'Objet du Filtre`,
    'FilterFailure': `la Panne du Filtre`,
    'default': () => {
        throw new Error("Class selector not known");
    }
}

const operators = ["OU", "ET"];

const attributes = [
    'path',
    'id',
    'comment',
    'is_ok',
    'value',
    'display_type',
    'ask_confirm'
]

const tests = {
    '<': '<',
    '>': '>',
    '<=': '<=',
    '>=': '>=',
    '=': '=',
    'is': 'est',
    'in': 'est dans',
    'in_or_equal': 'est dans/est',
    'is_for_user': 'est pour l\'utilisateur',
    'is_for_thing': 'est pour l\'objet',
    'pending_feedback': 'en attente de retours',
    'active': 'est actif',
    'contains': 'contient',
    'true': 'est vrai',
    'false': 'est faux',
    'True': 'est True'
}

const items = {
    'FilterThing': `l\'Objet`,
    'FilterFailure': `la Panne`,
    'Selector': `le Sélecteur d'ID`,
    'SourceThing': `l\'Objet Source`,
    'SourceThingUser': `l\'Utilisateur de l\'Objet Source`,
    'SourceFailure': `la Panne Source`,
    'SourceUser': `l\'Utilisateur Source`
}

const left = 1;
const right = 2;

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
        sentence = selector.slice(1).map(e => '(' + transcribeSelector(e) + ')').join(` <b>${operators[selector[0]]}</b> `);
    } else {
        for (const [key, value] of Object.entries(selector).sort(([keyA, valA], [keyB, valB]) => {
            const map = {  // The higher the number, the more to the left of the selector it will appear
                'class': 4,
                'attr': 3,
                'test': 2,
            }
            const newA = map[keyA] ?? 1;
            const newB = map[keyB] ?? 1;
            return newB - newA;
        })) {
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

function getRawSelectorValue() {
    const rawSelector = document.getElementById('raw_selector');
    return rawSelector.textContent;
}

function getParsedRawSelectorValue() {
    return JSON.parse(getRawSelectorValue());
}

function updateMaxArrayLength() {
    let selectorRepresentation = getParsedRawSelectorValue();
    let maxConditionArrayLength = Array.isArray(selectorRepresentation) ? selectorRepresentation.length - 1 : 2;
    document.querySelector('.selector_builder .side_selector input').setAttribute('max', maxConditionArrayLength.toString());
    document.querySelector('.selector_builder .selector_conditions input').setAttribute('max', maxConditionArrayLength.toString());
}

function updateRenderedSelector(selectorRepresentation) {
    const rawSelector = document.getElementById('raw_selector');
    const parsedSelectorRepresentation = JSON.parse(selectorRepresentation);
    rawSelector.textContent = selectorRepresentation;
    document.getElementById('rendered_selector').innerHTML = transcribeSelector(parsedSelectorRepresentation);
    document.getElementById('input').setAttribute('value', selectorRepresentation);
    document.querySelectorAll('.selector_builder .show_if_condition').forEach(
        e => e.style.display = (Array.isArray(parsedSelectorRepresentation)) ? 'initial' : 'none'
    );
}

function sideToEditIndex() {
    return parseInt(document.querySelector('.selector_builder .side_selector input').value);
}

function addCondition(condition_type) {
    let selectorRepresentation = getParsedRawSelectorValue();

    if (Array.isArray(selectorRepresentation)) {
        selectorRepresentation[0] = condition_type;
    } else {
        selectorRepresentation = [condition_type, selectorRepresentation, {}];
    }

    return JSON.stringify(selectorRepresentation);
}

function keepCondition(side_to_keep) {
    let selectorRepresentation = getParsedRawSelectorValue();

    if (Array.isArray(selectorRepresentation)) {
        selectorRepresentation = selectorRepresentation[side_to_keep];
    }

    return JSON.stringify(selectorRepresentation);
}

function updatePart(key, value) {
    let selectorRepresentation = getParsedRawSelectorValue();

    let editablePart = selectorRepresentation;
    if (Array.isArray(selectorRepresentation)) {
        editablePart = selectorRepresentation[sideToEditIndex()];
    }

    if (value) {
        editablePart[key] = value;
    } else {
        delete editablePart[key];
    }
    return JSON.stringify(selectorRepresentation);
}

function updateAttribute(attribute) {
    return updatePart('attr', attribute)
}

function updateTest(test) {
    return updatePart('test', test);
}

function updateItems(item) {
    return updatePart('class', item);
}

function updateValue(value, key) {
    // 'key' is either 'id' or 'value'
    return updatePart(key, value)
}