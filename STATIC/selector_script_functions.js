function html(txt) {
    return txt.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

var TESTS = [
    ["Incident concerne l'utilisateur connecté", { test: "is_for_user" }],
    ["Incident est actif", { test: "active" }],
    ["Incident concerne la panne", { test: "is", class: "FilterFailure" }],
    ["Incident concerne une panne du groupe", { test: "in_or_equal", class: "FilterFailure" }],
    ["Incident réparé et utilisateur non prévenu", { test: "pending_feedback" }],
    ["Incident concerne une chose du groupe", { test: "in_or_equal", class: "FilterThing" }],
    ["Incident concerne une chose (pas API)", { test: "is_for_thing" }],
    ["Incident non fixé (nombre de jours)", { test: "older_than" }],
    ["La panne déclenchée est dans le groupe", { test: "in_or_equal", class: "SourceFailure" }],
    ["La panne déclenchée est", { test: "is", class: "SourceFailure" }],
    ["L'utilisateur connecté est dans le groupe", { test: "in_or_equal", class: "SourceUser" }],
    /* ["L'utilisateur connecté est", { test: "is", class: "SourceUser" }], */
    ["L'utilisateur modifié est dans le groupe", { test: "in_or_equal", class: "SourceThingUser" }],
    ["Le sélecteur retourne vrai", { test: "true", class: "Selector" }],
    ["Le sélecteur retourne faux", { test: "false", class: "Selector" }],
    ["L'objet modifié est dans le groupe", { test: "in_or_equal", class: "SourceThing" }],
    ["Toujours vrai", { test: "True" }],
    ["Toujours faux", { test: "False" }]
];
function match(expr, test) {
    for (var attr in test)
        if (test[attr] != expr[attr])
            return;
    return true;
}
function editor(expr) {
    for (var i in TESTS) {
        if (match(expr, TESTS[i][1])) {
            var texts = ['<SELECT class="test" autocomplete="off">'];
            for (var j in TESTS)
                texts.push(`<OPTION value="${j}" ${j == i ? 'selected' : ''}>${html(TESTS[j][0])}</OPTION>`);
            texts.push('</SELECT>');
            if (TESTS[i][1].class) {
                var list = TESTS[i][1].class.replace(/.*(User|Thing|Failure|Selector)$/, '$1');
                texts.push(` <INPUT autocomplete="off" value="${html(expr.value || expr.id || '')}" list="datalist_${list}">`);
            }
            if (TESTS[i][1].test == 'older_than')
                texts.push(` <INPUT autocomplete="off" value="${html(expr.value || '')}">`);
            return texts.join('');
        }
    }
    return `<INPUT class="raw" autocomplete="off" style="width:calc(100% - 0.7em)" value="${html(JSON.stringify(expr))}">`;
}

var DATA = {};

function edit_selector(selector_id, expression) {
    var exprs = expression.slice(1);
    var operator = expression[0];
    var texts = [`<select class="and_or">
        <option ${operator ? '' : 'selected'} value="0">OU</option>
        <option ${operator ? 'selected' : ''} value="1">ET</option>
        </select>
        <ADD>+</ADD>
        `];
    texts.push('<OPE>');
    for (var expr of exprs) {
        texts.push('<REM>×</REM>');
        texts.push(editor(expr));
        texts.push('<BR>');
    }
    texts.push('</OPE> <SAV>Save</SAV>');
    return texts.join('');
}

function add_selector(selector_id, expression) {
    if (expression.length === undefined)
        expression = [0, expression];
    DATA[selector_id] = { current: expression, original: JSON.stringify(expression) };
    document.write(edit_selector(selector_id, expression));
}

function init() {
    var texts = [];
    for (var name in LISTS) {
        texts.push(`<DATALIST id="${name}">`);
        for (var i of LISTS[name])
            texts.push(`<OPTION>${html(i)}</OPTION>`);
        texts.push('</DATALIST>');
    }
    texts.push(`
        <style>
        TABLE {
            border-spacing: 0px;
        }
        TD {
            padding: 0.3em;
        }
        INPUT {
            vertical-align: bottom;
        }
        REM, ADD, SAV {
            display: inline;
            opacity: 0;
            cursor: pointer;
        }
        OPE {
            display: inline-block;
            border-left: 3px solid #000;
            border-radius: 0.7em;
            padding-left: 0.4em;
            vertical-align: middle;
        }
        TR:hover REM, TR:hover ADD, TD.changed SAV {
            opacity: 1;
        }
        REM {
            margin-left: -0.4em;
        }
        SAV {
            border: 1px solid #000;
            border-radius: 0.5em;
            background: #EEE;
            padding: 0.3em;
        }
    </style>`);
    return texts.join('');
}

window.onchange = window.onclick = window.onkeyup = function (event) {
    var elm = event.target;
    var td = elm;
    while (td && td.tagName != 'TD')
        td = td.parentNode;
    var tr = td;
    while (tr && tr.tagName != 'TR')
        tr = tr.parentNode;
    if (!tr)
        return;
    if (elm.onclick || elm.onchange || elm.onkeypress)
        return;
    var selector_id = tr.cells[0].textContent;
    var index = 1;
    for (var i = elm; i; i = i.previousSibling)
        if (i.tagName == 'BR')
            index++;
    var expr = DATA[selector_id].current;
    if (elm.className == 'and_or' && event.type == 'change')
        expr[0] = Number(elm.value);
    else if (elm.className == 'test' && event.type == 'change')
        expr[index] = { ...TESTS[elm.value][1] };
    else if (elm.tagName == 'REM' && event.type == 'click')
        expr.splice(index, 1);
    else if (elm.tagName == 'ADD' && event.type == 'click')
        expr.push({ 'test': 'True' });
    else if (elm.tagName == 'SAV' && event.type == 'click') {
        var url = [
            `${location.origin}${location.pathname}?thing-id=${encodeURIComponent(selector_id)}`,
            'failure-id=$selector-expression',
            'what=selector',
            'additional-info=' + encodeURIComponent(JSON.stringify(expr)),
            'secret=' + secret];
        var iframe = document.createElement('IFRAME');
        iframe.onload = function () {
            DATA[selector_id].original = expr;
            td.className = '';
            td.innerHTML = edit_selector(selector_id, expr);
        };
        iframe.onerror = function () {
            iframe.style.display = 'block';
        };
        iframe.src = url.join('&');
        iframe.style.display = 'none';
        elm.parentNode.appendChild(iframe);
        return;
    } else if (elm.tagName == 'INPUT' && event.key == 'Escape')
        if (expr.class == 'Selector')
            elm.value = expr[index].id;
        else
            elm.value = expr[index].value;
    else if (elm.tagName == 'INPUT' && event.type == 'change') {
        if (elm.className == 'raw') {
            try { expr[index] = JSON.parse(elm.value); }
            catch (e) { alert("Formule inchangée car invalide"); }
        } else {
            if (elm.getAttribute('list')) {
                if (LISTS[elm.getAttribute('list')].includes(elm.value))
                    if (expr.class == 'Selector')
                        expr[index].id = elm.value;
                    else
                        expr[index].value = elm.value;
                else
                    alert("Valeur inchangée car cela n'existe pas");
            }
            else {
                if (isNaN(elm.value))
                    alert("Valeur inchangée car non flottante");
                else
                    expr[index].value = elm.value;
            }
        }
    } else
        return;
    td.innerHTML = edit_selector(selector_id, expr);
    if (JSON.stringify(expr) != DATA[selector_id].original)
        td.className = 'changed';
    else
        td.className = '';
}
document.write(init());
