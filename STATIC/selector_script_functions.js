function handleTestCases(testCases, value) {
    let sentence = '';
    let correctTestCase = testCases[value];
    if (correctTestCase === undefined) {
        correctTestCase = testCases["default"];
    }
    if (typeof correctTestCase === 'function') {
        sentence += correctTestCase();
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
        sentence = '(' + transcribeSelector(selector[1]) + ')' + [" <b>OU</b> ", " <b>ET</b> "][selector[0]] + '(' + transcribeSelector(selector[2]) + ')';
    } else {
        for (const [key, value] of Object.entries(selector)) {
            if (key === 'test') {
                const testCases = {
                    'active': 'L\'Incident est actif',
                    'contains': ` contient <i>${selector.value}</i>`,
                    'true': ' est vrai',
                    'false': ' est faux',
                    'pending_feedback': ' en attente de retours',
                    'is_for_thing': ' est pour l\'objet',
                    'is_for_user': ' est pour l\'utilisateur',
                    'in': () => {
                        if (selector?.class === 'User' || selector?.class === 'Failure') {
                            return ` est dans le groupe <i>${selector.value}</i>`;
                        } else {
                            return ` est dans <i>${selector.value}</i>`;
                        }
                    },
                    'in_or_equal': ` est dans/est <i>${selector.value}</i>`,
                    'is': ` est <i>${selector.value}</i>`,
                    'True': ' est True',
                    'default': () => {
                        if (['<','>','<=','>=','='].includes(value)) {
                            return ` ${value} <i>${selector.value}</i>`;
                        } else {
                            throw new Error("Test selector not known");
                        }
                    }
                }
                sentence += handleTestCases(testCases, value);
            }
            else if (key === 'class') {
                const testCases = {
                    'Incident': `l\'Incident`,
                    'Thing': `l\'Objet`,
                    'Failure': `la Panne`,
                    'User': `l\'Utilisateur`,
                    'Selector': `le Sélecteur d'ID "${selector.id}"`,
                    'SourceThing': `l\'Objet Source`,
                    'SourceFailure': `la Panne Source`,
                    'SourceUser': `l\'Utilisateur Source`,
                    'default': () => {
                        throw new Error("Class selector not known");
                    }
                }
                sentence += handleTestCases(testCases, value);
            }
            else if (key === 'attr') {
                sentence += ` <i>(attribut "${value}")</i>`;
            }
        }
    }
    sentence = sentence.replaceAll(/^ +/g, '');
    return sentence[0].toUpperCase() + sentence.slice(1);
}