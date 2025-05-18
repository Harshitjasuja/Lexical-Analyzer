// Language definitions
        const languageDefinitions = {
            java: {
                keywords: ['abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const', 
                           'continue', 'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 'float', 
                           'for', 'if', 'goto', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native', 
                           'new', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'strictfp', 
                           'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'try', 'void', 
                           'volatile', 'while', 'true', 'false', 'null'],
                operators: ['+', '-', '*', '/', '%', '++', '--', '==', '!=', '>', '<', '>=', '<=', '&&', '||', 
                            '!', '&', '|', '^', '~', '<<', '>>', '>>>', '+=', '-=', '*=', '/=', '%=', '&=', '|=', 
                            '^=', '<<=', '>>=', '>>>=', '=', '->'],
                separators: [',', ';', '.', ':', '(', ')', '[', ']', '{', '}'],
                commentStart: ['/*', '//'],
                commentEnd: ['*/'],
                stringDelimiters: ['"', "'"],
                errorPatterns: {
                    unclosedString: /("(?:[^"\\]|\\.)*$)|('(?:[^'\\]|\\.)*$)/,
                    unclosedComment: /\/\*(?:[^*]|\*(?!\/))*$/,
                    invalidIdentifier: /[0-9]+[a-zA-Z_]+/,
                    unmatchedParenthesis: /\([^)]*$/,
                    unmatchedBrace: /\{[^}]*$/,
                    unmatchedBracket: /\[[^\]]*$/
                },
                errorSuggestions: {
                    unclosedString: "Add closing quotation mark",
                    unclosedComment: "Add closing comment symbol */",
                    invalidIdentifier: "Identifiers cannot start with a number",
                    unmatchedParenthesis: "Add closing parenthesis )",
                    unmatchedBrace: "Add closing brace }",
                    unmatchedBracket: "Add closing bracket ]"
                }
            },
            python: {
                keywords: ['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 
                           'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 
                           'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 
                           'try', 'while', 'with', 'yield'],
                operators: ['+', '-', '*', '/', '//', '%', '**', '==', '!=', '>', '<', '>=', '<=', 'and', 'or', 
                            'not', 'is', 'in', '+=', '-=', '*=', '/=', '//=', '%=', '**=', '&=', '|=', '^=', '>>=', 
                            '<<=', '=', '&', '|', '^', '~', '<<', '>>'],
                separators: [',', ':', '.', ';', '(', ')', '[', ']', '{', '}'],
                commentStart: ['#'],
                commentEnd: ['\n'],
                stringDelimiters: ['"', "'", '"""', "'''"],
                errorPatterns: {
                    unclosedString: /("(?:[^"\\]|\\.)*$)|('(?:[^'\\]|\\.)*$)|("""(?:[^"\\]|\\.)*$)|('''(?:[^'\\]|\\.)*$)/,
                    indentationError: /^ +\t/m,
                    unmatchedParenthesis: /\([^)]*$/,
                    unmatchedBrace: /\{[^}]*$/,
                    unmatchedBracket: /\[[^\]]*$/
                },
                errorSuggestions: {
                    unclosedString: "Add closing quotation mark",
                    indentationError: "Don't mix spaces and tabs in indentation",
                    unmatchedParenthesis: "Add closing parenthesis )",
                    unmatchedBrace: "Add closing brace }",
                    unmatchedBracket: "Add closing bracket ]"
                }
            },
            cpp: {
                keywords: ['alignas', 'alignof', 'and', 'and_eq', 'asm', 'auto', 'bitand', 'bitor', 'bool', 'break', 
                           'case', 'catch', 'char', 'char8_t', 'char16_t', 'char32_t', 'class', 'compl', 'concept', 
                           'const', 'consteval', 'constexpr', 'constinit', 'const_cast', 'continue', 'co_await', 
                           'co_return', 'co_yield', 'decltype', 'default', 'delete', 'do', 'double', 'dynamic_cast', 
                           'else', 'enum', 'explicit', 'export', 'extern', 'false', 'float', 'for', 'friend', 'goto', 
                           'if', 'inline', 'int', 'long', 'mutable', 'namespace', 'new', 'noexcept', 'not', 'not_eq', 
                           'nullptr', 'operator', 'or', 'or_eq', 'private', 'protected', 'public', 'reflexpr', 
                           'register', 'reinterpret_cast', 'requires', 'return', 'short', 'signed', 'sizeof', 'static', 
                           'static_assert', 'static_cast', 'struct', 'switch', 'template', 'this', 'thread_local', 
                           'throw', 'true', 'try', 'typedef', 'typeid', 'typename', 'union', 'unsigned', 'using', 
                           'virtual', 'void', 'volatile', 'wchar_t', 'while', 'xor', 'xor_eq'],
                operators: ['+', '-', '*', '/', '%', '++', '--', '==', '!=', '>', '<', '>=', '<=', '&&', '||', 
                            '!', '&', '|', '^', '~', '<<', '>>', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', 
                            '<<=', '>>=', '=', '->','::', '.*', '->*'],
                separators: [',', ';', '.', ':', '(', ')', '[', ']', '{', '}'],
                commentStart: ['/*', '//'],
                commentEnd: ['*/'],
                stringDelimiters: ['"', "'"],
                errorPatterns: {
                    unclosedString: /("(?:[^"\\]|\\.)*$)|('(?:[^'\\]|\\.)*$)/,
                    unclosedComment: /\/\*(?:[^*]|\*(?!\/))*$/,
                    invalidIdentifier: /[0-9]+[a-zA-Z_]+/,
                    unmatchedParenthesis: /\([^)]*$/,
                    unmatchedBrace: /\{[^}]*$/,
                    unmatchedBracket: /\[[^\]]*$/
                },
                errorSuggestions: {
                    unclosedString: "Add closing quotation mark",
                    unclosedComment: "Add closing comment symbol */",
                    invalidIdentifier: "Identifiers cannot start with a number",
                    unmatchedParenthesis: "Add closing parenthesis )",
                    unmatchedBrace: "Add closing brace }",
                    unmatchedBracket: "Add closing bracket ]"
                }
            }
        };

        // Sample code snippets for demonstration
        const sampleCode = {
            java: `public class HelloWorld {
    public static void main(String[] args) {
        // This is a comment
        int num1 = 10;
        int num2 = 20;
        int sum = num1 + num2;
        System.out.println("Sum is: " + sum);
        
        if (sum > 25) {
            System.out.println("Sum is greater than 25");
        } else {
            System.out.println("Sum is less than or equal to 25");
        }
        
        /* This is a
           multi-line comment */
        for (int i = 0; i < 5; i++) {
            System.out.println("Count: " + i);
        }
    }
}`,
            python: `# Define a function
def calculate_sum(a, b):
    """
    This function calculates the sum of two numbers
    and returns the result
    """
    return a + b

# Main program
if __name__ == "__main__":
    # Initialize variables
    num1 = 10
    num2 = 20
    
    # Calculate sum
    result = calculate_sum(num1, num2)
    
    # Print result
    print(f"The sum of {num1} and {num2} is: {result}")
    
    # Conditional statement
    if result > 25:
        print("Result is greater than 25")
    else:
        print("Result is less than or equal to 25")
        
    # Loop example
    for i in range(5):
        print(f"Count: {i}")`,
            cpp: `#include <iostream>
#include <string>
using namespace std;

// Define a function to calculate sum
int calculateSum(int a, int b) {
    return a + b;
}

int main() {
    // Initialize variables
    int num1 = 10;
    int num2 = 20;
    
    // Calculate sum
    int sum = calculateSum(num1, num2);
    
    // Output result
    cout << "Sum is: " << sum << endl;
    
    // Conditional statement
    if (sum > 25) {
        cout << "Sum is greater than 25" << endl;
    } else {
        cout << "Sum is less than or equal to 25" << endl;
    }
    
    /* This is a
       multi-line comment */
    for (int i = 0; i < 5; i++) {
        cout << "Count: " << i << endl;
    }
    
    return 0;
}`
        };

        // Initialize CodeMirror
        let editor = CodeMirror(document.getElementById('code-editor'), {
            lineNumbers: true,
            theme: 'material',
            mode: 'text/x-java',
            indentUnit: 4,
            smartIndent: true,
            tabSize: 4,
            indentWithTabs: false,
            lineWrapping: true,
            extraKeys: {"Tab": "indentMore", "Shift-Tab": "indentLess"}
        });

        // Set initial sample code
        editor.setValue(sampleCode.java);

        // Language select handler
        document.getElementById('language-select').addEventListener('change', function() {
            const language = this.value;
            switch(language) {
                case 'java':
                    editor.setOption('mode', 'text/x-java');
                    break;
                case 'python':
                    editor.setOption('mode', 'text/x-python');
                    break;
                case 'cpp':
                    editor.setOption('mode', 'text/x-c++src');
                    break;
            }
            editor.setValue(sampleCode[language]);
        });

        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', function() {
                // Remove active class from all tabs and contents
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked tab
                this.classList.add('active');
                
                // Show corresponding content
                const tabContent = document.getElementById(this.dataset.tab + '-tab');
                tabContent.classList.add('active');
            });
        });

        // Load sample code button
        document.getElementById('sample-btn').addEventListener('click', function() {
            const language = document.getElementById('language-select').value;
            editor.setValue(sampleCode[language]);
        });

        // Clear button
        document.getElementById('clear-btn').addEventListener('click', function() {
            editor.setValue('');
            document.getElementById('token-display').innerHTML = '';
            document.getElementById('error-list').innerHTML = '<p>No errors found.</p>';
            updateStatistics({});
            clearVisualization();
        });

        // Analyze button
        document.getElementById('analyze-btn').addEventListener('click', function() {
            const code = editor.getValue();
            const language = document.getElementById('language-select').value;
            
            // Clear previous results
            document.getElementById('token-display').innerHTML = '';
            document.getElementById('error-list').innerHTML = '';
            
            // Perform lexical analysis
            const { tokens, errors } = lexicalAnalysis(code, language);
            
            // Display tokens
            displayTokens(tokens);
            
            // Display errors
            displayErrors(errors);
            
            // Update statistics
            updateStatistics(calculateStatistics(tokens, errors));
            
            // Update visualization
            updateVisualization(tokens, language);
        });

        // Lexical Analysis function
        function lexicalAnalysis(code, language) {
            const languageDef = languageDefinitions[language];
            const tokens = [];
            const errors = [];
            
            let position = 0;
            let line = 1;
            let column = 1;
            
            // Helper function to update position
            function updatePosition(char) {
                if (char === '\n') {
                    line++;
                    column = 1;
                } else {
                    column++;
                }
                position++;
            }
            
            // Helper function to check if character is alphanumeric or underscore
            function isAlphaNumeric(char) {
                return /[a-zA-Z0-9_]/.test(char);
            }
            
            // Helper function to check if character is whitespace
            function isWhitespace(char) {
                return /\s/.test(char);
            }
            
            // Helper function to check if string is a number
            function isNumber(str) {
                return /^[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?$/.test(str);
            }
            
            // Helper function to check if operator starts with character
            function startsWithOperator(str) {
                return languageDef.operators.some(op => op.startsWith(str));
            }
            
            // Helper function to get maximum matching operator
            function getMaxOperator(str) {
                let maxOp = '';
                for (const op of languageDef.operators) {
                    if (str.startsWith(op) && op.length > maxOp.length) {
                        maxOp = op;
                    }
                }
                return maxOp;
            }
            
            // Check for errors in the entire code
            function checkForErrors() {
                // Check for unclosed strings
                if (languageDef.errorPatterns.unclosedString.test(code)) {
                    errors.push({
                        type: 'unclosedString',
                        message: 'Unclosed string literal',
                        line: line,
                        column: column,
                        suggestion: languageDef.errorSuggestions.unclosedString
                    });
                }
                
                // Check for unclosed comments (for languages that support block comments)
                if (languageDef.errorPatterns.unclosedComment && languageDef.errorPatterns.unclosedComment.test(code)) {
                    errors.push({
                        type: 'unclosedComment',
                        message: 'Unclosed comment',
                        line: line,
                        column: column,
                        suggestion: languageDef.errorSuggestions.unclosedComment
                    });
                }
                
                // Check for unmatched parentheses, braces, brackets
                if (languageDef.errorPatterns.unmatchedParenthesis.test(code)) {
                    errors.push({
                        type: 'unmatchedParenthesis',
                        message: 'Unmatched parenthesis',
                        line: line,
                        column: column,
                        suggestion: languageDef.errorSuggestions.unmatchedParenthesis
                    });
                }
                
                if (languageDef.errorPatterns.unmatchedBrace.test(code)) {
                    errors.push({
                        type: 'unmatchedBrace',
                        message: 'Unmatched brace',
                        line: line,
                        column: column,
                        suggestion: languageDef.errorSuggestions.unmatchedBrace
                    });
                }
                
                if (languageDef.errorPatterns.unmatchedBracket.test(code)) {
                    errors.push({
                        type: 'unmatchedBracket',
                        message: 'Unmatched bracket',
                        line: line,
                        column: column,
                        suggestion: languageDef.errorSuggestions.unmatchedBracket
                    });
                }
                
                // Python-specific: Check for indentation errors
                if (language === 'python' && languageDef.errorPatterns.indentationError.test(code)) {
                    errors.push({
                        type: 'indentationError',
                        message: 'Mixed spaces and tabs in indentation',
                        line: line,
                        column: column,
                        suggestion: languageDef.errorSuggestions.indentationError
                    });
                }
            }
            
            // Check for errors first
            checkForErrors();
            
            // Main lexical analysis loop
            while (position < code.length) {
                const char = code[position];
                let startPos = position;
                let startLine = line;
                let startColumn = column;
                
                // Skip whitespace
                if (isWhitespace(char)) {
                    updatePosition(char);
                    continue;
                }
                
                // Check for comments
                let isComment = false;
                for (const commentStart of languageDef.commentStart) {
                    if (code.substring(position).startsWith(commentStart)) {
                        isComment = true;
                        let commentText = commentStart;
                        position += commentStart.length;
                        column += commentStart.length;
                        
                        let endComment = false;
                        let commentEndPattern;
                        
                        // Single-line comments end at newline
                        if (commentStart === '//' || commentStart === '#') {
                            commentEndPattern = '\n';
                        } else {
                            // Multi-line comments end with specific pattern
                            commentEndPattern = languageDef.commentEnd[0]; // Assumes multi-line comments use first end pattern
                        }
                        
                        while (position < code.length && !endComment) {
                            if (code.substring(position).startsWith(commentEndPattern)) {
                                commentText += code.substring(position, position + commentEndPattern.length);
                                position += commentEndPattern.length;
                                column += commentEndPattern.length;
                                endComment = true;
                                break;
                            }
                            commentText += code[position];
                            updatePosition(code[position]);
                        }
                        
                        tokens.push({
                            type: 'comment',
                            value: commentText,
                            line: startLine,
                            column: startColumn
                        });
                        
                        break;
                    }
                }
                
                if (isComment) continue;
                
                // Check for string literals
                let isString = false;
                for (const delimiter of languageDef.stringDelimiters) {
                    if (code.substring(position).startsWith(delimiter)) {
                        isString = true;
                        let stringText = delimiter;
                        position += delimiter.length;
                        column += delimiter.length;
                        
                        let endString = false;
                        let escaped = false;
                        
                        while (position < code.length && !endString) {
                            const currentChar = code[position];
                            
                            stringText += currentChar;
                            
                            if (escaped) {
                                escaped = false;
                            } else if (currentChar === '\\') {
                                escaped = true;
                            } else if (code.substring(position).startsWith(delimiter) && 
                                     (delimiter.length === 1 || code.substring(position, position + delimiter.length) === delimiter)) {
                                endString = true;
                                if (delimiter.length > 1) {
                                    stringText += code.substring(position + 1, position + delimiter.length);
                                    position += delimiter.length;
                                    column += delimiter.length;
                                } else {
                                    position++;
                                    column++;
                                }
                                break;
                            }
                            
                            if (!endString) {
                                updatePosition(currentChar);
                            }
                        }
                        
                        if (!endString) {
                            // Handle unclosed string
                            tokens.push({
                                type: 'error',
                                value: stringText,
                                errorType: 'unclosedString',
                                line: startLine,
                                column: startColumn
                            });
                            
                            errors.push({
                                type: 'unclosedString',
                                message: 'Unclosed string literal',
                                line: startLine,
                                column: startColumn,
                                suggestion: languageDef.errorSuggestions.unclosedString
                            });
                        } else {
                            tokens.push({
                                type: 'literal',
                                subtype: 'string',
                                value: stringText,
                                line: startLine,
                                column: startColumn
                            });
                        }
                        
                        break;
                    }
                }
                
                if (isString) continue;
                
                // Check for numeric literals
                if (/[0-9.]/.test(char)) {
                    let numStr = '';
                    let isInvalid = false;
                    let hasDecimal = false;
                    
                    while (position < code.length && (/[0-9.]/.test(code[position]) || 
                           (numStr.length > 0 && /[eE]/.test(code[position])) ||
                           (numStr.length > 0 && /[eE]/.test(code[position-1]) && /[+-]/.test(code[position])))) {
                        
                        if (code[position] === '.') {
                            if (hasDecimal) {
                                isInvalid = true;
                            }
                            hasDecimal = true;
                        }
                        
                        numStr += code[position];
                        updatePosition(code[position]);
                    }
                    
                    // Check if valid number
                    if (isNumber(numStr)) {
                        tokens.push({
                            type: 'literal',
                            subtype: 'number',
                            value: numStr,
                            line: startLine,
                            column: startColumn
                        });
                    } else {
                        tokens.push({
                            type: 'error',
                            value: numStr,
                            errorType: 'invalidNumber',
                            line: startLine,
                            column: startColumn
                        });
                        
                        errors.push({
                            type: 'invalidNumber',
                            message: 'Invalid numeric literal',
                            line: startLine,
                            column: startColumn,
                            suggestion: 'Check numeric format'
                        });
                    }
                    
                    continue;
                }
                
                // Check for identifiers and keywords
                if (/[a-zA-Z_]/.test(char)) {
                    let identifier = '';
                    
                    while (position < code.length && isAlphaNumeric(code[position])) {
                        identifier += code[position];
                        updatePosition(code[position]);
                    }
                    
                    if (languageDef.keywords.includes(identifier)) {
                        tokens.push({
                            type: 'keyword',
                            value: identifier,
                            line: startLine,
                            column: startColumn
                        });
                    } else {
                        tokens.push({
                            type: 'identifier',
                            value: identifier,
                            line: startLine,
                            column: startColumn
                        });
                    }
                    
                    continue;
                }
                
                // Check for operators
                let opStr = char;
                if (startsWithOperator(opStr)) {
                    const maxOp = getMaxOperator(code.substring(position));
                    
                    if (maxOp) {
                        tokens.push({
                            type: 'operator',
                            value: maxOp,
                            line: startLine,
                            column: startColumn
                        });
                        
                        position += maxOp.length;
                        column += maxOp.length;
                        continue;
                    }
                }
                
                // Check for separators
                if (languageDef.separators.includes(char)) {
                    tokens.push({
                        type: 'separator',
                        value: char,
                        line: startLine,
                        column: startColumn
                    });
                    
                    updatePosition(char);
                    continue;
                }
                
                // Unknown character (error)
                tokens.push({
                    type: 'error',
                    value: char,
                    errorType: 'unknownChar',
                    line: startLine,
                    column: startColumn
                });
                
                errors.push({
                    type: 'unknownChar',
                    message: `Unknown character: '${char}'`,
                    line: startLine,
                    column: startColumn,
                    suggestion: 'Remove or replace the invalid character'
                });
                
                updatePosition(char);
            }
            
            return { tokens, errors };
        }

        // Function to display tokens
        function displayTokens(tokens) {
            const tokenDisplay = document.getElementById('token-display');
            
            tokens.forEach(token => {
                const tokenElement = document.createElement('div');
                tokenElement.className = `token ${token.type}`;
                
                const tokenTypeElement = document.createElement('div');
                tokenTypeElement.className = 'token-type';
                tokenTypeElement.textContent = token.type;
                
                const tokenValueElement = document.createElement('div');
                tokenValueElement.className = 'token-value';
                tokenValueElement.textContent = token.value;
                
                const tokenDetailsElement = document.createElement('div');
                tokenDetailsElement.className = 'token-details';
                tokenDetailsElement.innerHTML = `
                    <div>Type: ${token.type}</div>
                    ${token.subtype ? `<div>Subtype: ${token.subtype}</div>` : ''}
                    <div>Value: "${token.value}"</div>
                    <div>Line: ${token.line}</div>
                    <div>Column: ${token.column}</div>
                `;
                
                tokenElement.appendChild(tokenTypeElement);
                tokenElement.appendChild(tokenValueElement);
                tokenElement.appendChild(tokenDetailsElement);
                
                tokenDisplay.appendChild(tokenElement);
            });
        }

        // Function to display errors
        function displayErrors(errors) {
            const errorList = document.getElementById('error-list');
            
            if (errors.length === 0) {
                errorList.innerHTML = '<p>No errors found.</p>';
                return;
            }
            
            errorList.innerHTML = '';
            
            errors.forEach(error => {
                const errorItem = document.createElement('div');
                errorItem.className = 'error-item';
                
                errorItem.innerHTML = `
                    <div class="error-position">Line ${error.line}, Column ${error.column}</div>
                    <div>${error.message}</div>
                    <div class="error-suggestion">Suggestion: ${error.suggestion}</div>
                `;
                
                errorList.appendChild(errorItem);
            });
        }

        // Function to calculate statistics
        function calculateStatistics(tokens, errors) {
            const stats = {
                totalTokens: tokens.length,
                keywords: 0,
                identifiers: 0,
                literals: 0,
                operators: 0,
                separators: 0,
                comments: 0,
                errors: errors.length
            };
            
            tokens.forEach(token => {
                switch(token.type) {
                    case 'keyword': 
                        stats.keywords++; 
                        break;
                    case 'identifier': 
                        stats.identifiers++; 
                        break;
                    case 'literal': 
                        stats.literals++; 
                        break;
                    case 'operator': 
                        stats.operators++; 
                        break;
                    case 'separator': 
                        stats.separators++; 
                        break;
                    case 'comment': 
                        stats.comments++; 
                        break;
                }
            });
            
            return stats;
        }

        // Function to update statistics display
        function updateStatistics(stats) {
            document.getElementById('total-tokens').textContent = stats.totalTokens || 0;
            document.getElementById('keywords').textContent = stats.keywords || 0;
            document.getElementById('identifiers').textContent = stats.identifiers || 0;
            document.getElementById('literals').textContent = stats.literals || 0;
            document.getElementById('operators').textContent = stats.operators || 0;
            document.getElementById('separators').textContent = stats.separators || 0;
            document.getElementById('comments').textContent = stats.comments || 0;
            document.getElementById('error-count').textContent = stats.errors || 0;
        }

        // Function to clear visualization
        function clearVisualization() {
            const container = document.getElementById('state-machine-container');
            container.innerHTML = '';
        }

        // Function to update the visualization
        function updateVisualization(tokens, language) {
            const container = document.getElementById('state-machine-container');
            container.innerHTML = '';
            
            // Initialize D3 visualization
            const width = container.clientWidth;
            const height = container.clientHeight;
            
            const svg = d3.select('#state-machine-container')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
                
            // Create groups for nodes and links
            const linkGroup = svg.append('g').attr('class', 'links');
            const nodeGroup = svg.append('g').attr('class', 'nodes');
            
            // Prepare data for visualization
            const tokenTypes = ['start', ...new Set(tokens.map(token => token.type))];
            const nodes = tokenTypes.map(type => ({
                id: type,
                label: type === 'start' ? 'Start' : type.charAt(0).toUpperCase() + type.slice(1),
                count: type === 'start' ? 1 : tokens.filter(t => t.type === type).length
            }));
            
            // Create links between sequential tokens
            const links = [];
            let prevType = 'start';
            
            tokens.forEach(token => {
                const linkExists = links.some(link => 
                    link.source === prevType && link.target === token.type
                );
                
                if (!linkExists) {
                    links.push({
                        source: prevType,
                        target: token.type,
                        value: 1
                    });
                } else {
                    const link = links.find(link => 
                        link.source === prevType && link.target === token.type
                    );
                    link.value++;
                }
                
                prevType = token.type;
            });
            
            // Create force simulation
            const simulation = d3.forceSimulation(nodes)
                .force('link', d3.forceLink(links).id(d => d.id).distance(100))
                .force('charge', d3.forceManyBody().strength(-200))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('collision', d3.forceCollide().radius(50));
            
            // Create links
            const link = linkGroup.selectAll('line')
                .data(links)
                .enter()
                .append('path')
                .attr('stroke', '#999')
                .attr('stroke-opacity', 0.6)
                .attr('stroke-width', d => Math.sqrt(d.value) * 2)
                .attr('fill', 'none')
                .attr('marker-end', 'url(#arrow)');
            
            // Define arrow marker
            svg.append('defs').append('marker')
                .attr('id', 'arrow')
                .attr('viewBox', '0 -5 10 10')
                .attr('refX', 20)
                .attr('refY', 0)
                .attr('markerWidth', 6)
                .attr('markerHeight', 6)
                .attr('orient', 'auto')
                .append('path')
                .attr('d', 'M0,-5L10,0L0,5')
                .attr('fill', '#999');
            
            // Node color scale
            const colorScale = d3.scaleOrdinal()
                .domain(tokenTypes)
                .range(['#4a6fa5', '#7986cb', '#4db6ac', '#ffb74d', '#e57373', '#9e9e9e', '#90a4ae', '#f44336']);
            
            // Create nodes
            const node = nodeGroup.selectAll('circle')
                .data(nodes)
                .enter()
                .append('g')
                .attr('class', 'node')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));
            
            node.append('circle')
                .attr('r', d => Math.max(30, Math.sqrt(d.count) * 8))
                .attr('fill', d => colorScale(d.id))
                .attr('stroke', '#fff')
                .attr('stroke-width', 1.5);
            
            node.append('text')
                .attr('dy', '.35em')
                .attr('text-anchor', 'middle')
                .attr('fill', 'white')
                .style('font-size', '12px')
                .style('font-weight', 'bold')
                .text(d => d.label);
            
            node.append('text')
                .attr('dy', '2em')
                .attr('text-anchor', 'middle')
                .attr('fill', 'white')
                .style('font-size', '10px')
                .text(d => d.id !== 'start' ? `Count: ${d.count}` : '');
            
            // Update positions on simulation tick
            simulation.on('tick', () => {
                link.attr('d', function(d) {
                    const dx = d.target.x - d.source.x;
                    const dy = d.target.y - d.source.y;
                    const dr = Math.sqrt(dx * dx + dy * dy);
                    
                    // Create a curved path
                    return `M${d.source.x},${d.source.y}A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
                });
                
                node.attr('transform', d => `translate(${d.x},${d.y})`);
                
                // Keep nodes within bounds
                nodes.forEach(d => {
                    const radius = Math.max(30, Math.sqrt(d.count) * 8);
                    d.x = Math.max(radius, Math.min(width - radius, d.x));
                    d.y = Math.max(radius, Math.min(height - radius, d.y));
                });
            });
            
            // Functions for dragging nodes
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }
            
            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }
            
            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }
        }

        // Initialize with default sample
        document.getElementById('analyze-btn').click();