# Math markup reference

Text between `$` signs in any label, title, note or caption is typeset as mathematics. The syntax is a subset of TeX. Math is drawn as vector outlines from a bundled open-licensed font (STIX Two Math), so it looks the same in every browser, in PNG and in print.

```python
d.shape(r"**Policy**\n$\Pi(E_t, E_{t+1}) \to \{\mathrm{allow}, \mathrm{deny}\}$", 260, 70)
d.text(r"$\Omega_{\mathrm{safe}} = \bigcap_{k} \Omega_k$", size=16)
```

Use a raw string (`r"..."`) or double the backslashes. A literal dollar sign is `\$`; a lone `$` with no partner (`"Under $50k"`) is left as text.

Anything outside this reference raises `MathError` naming the command, instead of drawing something wrong. To check a formula before using it:

```python
from diagrams_as_code.text import TextStyle, layout

layout(r"$\theta \leftarrow \theta - \eta \nabla_\theta L$", TextStyle(size=13))
```

## Basics

| Write | Meaning |
|---|---|
| `x`, `E`, `f` | letters are set in math italic |
| `0`–`9` | digits are upright |
| `x_i`, `x_{t+1}` | subscript: one character, or a `{group}` |
| `x^2`, `e^{-st}` | superscript |
| `x_i^2` | both |
| `{...}` | a group, treated as one item |
| `\{`, `\}` | literal braces |
| `+ - * / = < > ( ) [ ] \| , ; : ! ' .` | typed as they are, spaced by their role |

Spacing follows the role of each symbol: binary operators and relations get space around them, punctuation gets space after it, and scripts are set tight.

## Text and fonts in math

| Write | Result |
|---|---|
| `\mathrm{safe}`, `\text{safe}`, `\textrm{safe}` | upright text |
| `\mathbf{R}`, `\textbf{R}` | bold upright |
| `\mathit{max}` | italic as a word, not as a product of letters |
| `\operatorname{rank}` | upright, spaced as an operator |
| `\mathbb{R}` | blackboard bold; `R N Z Q C` only |

## Greek

Lowercase: `\alpha \beta \gamma \delta \epsilon \zeta \eta \theta \iota \kappa \lambda \mu \nu \xi \omicron \pi \rho \varsigma \sigma \tau \upsilon \phi \chi \psi \omega`, and the variants `\varepsilon \vartheta \varphi \varrho \varpi`.

Uppercase: `\Gamma \Delta \Theta \Lambda \Xi \Pi \Sigma \Upsilon \Phi \Psi \Omega`. The other capitals are the Latin letters.

## Symbols

| Kind | Commands |
|---|---|
| Ordinary | `\partial \nabla \infty \forall \exists \nexists \emptyset \ell \hbar \top \bot \neg \lnot \angle \prime \ldots \dots \cdots \vdots \vert \Vert` |
| Binary operators | `\pm \mp \times \div \cdot \ast \circ \bullet \land \wedge \lor \vee \cap \cup \setminus \oplus \ominus \otimes \odot \sqcap \sqcup \uplus \diamond` |
| Relations | `\leq \le \geq \ge \neq \ne \equiv \approx \sim \simeq \cong \propto \ll \gg \prec \succ \preceq \succeq \triangleq \coloneqq` |
| Sets | `\in \notin \ni \subset \supset \subseteq \supseteq \subsetneq \supsetneq \sqsubseteq \sqsupseteq` |
| Logic and geometry | `\mid \parallel \perp \vdash \dashv \models` |
| Arrows | `\to \rightarrow \leftarrow \gets \leftrightarrow \uparrow \downarrow \mapsto \Rightarrow \Leftarrow \Leftrightarrow \implies \iff \longrightarrow \longleftarrow \leadsto \rightsquigarrow` |
| Delimiters | `\langle \rangle \lceil \rceil \lfloor \rfloor \lbrace \rbrace` |
| Punctuation | `\colon` |

## Functions and big operators

Named functions are set upright: `\min \max \sup \inf \lim \arg \argmin \argmax \log \ln \exp \sin \cos \tan \det \dim \ker \Pr \gcd \deg`.

Big operators: `\sum \prod \coprod \int \oint \bigcap \bigcup \bigwedge \bigvee`. Their limits are set underneath and above:

```text
$\sum_{i=1}^{n} x_i$        $\bigcap_{k} \Omega_k$
```

Add `\nolimits` to set them beside the operator, or `\limits` to force them underneath:

```text
$\sum\nolimits_{i} x_i$
```

## Spaces

| Write | Width |
|---|---|
| `\,` | thin |
| `\:` | medium |
| `\;` | thick |
| `\!` | negative thin |
| `\ ` (backslash, space) | a word space |
| `\quad`, `\qquad` | one em, two ems |

`\left`, `\right`, `\displaystyle` and `\textstyle` are accepted and ignored, so formulas pasted from a paper need less editing. Delimiters do not grow.

## Not supported

These raise `MathError`:

| Not supported | Write instead |
|---|---|
| `\frac{a}{b}` | `a / b`, or `a b^{-1}` |
| `\sqrt{x}` | `x^{1/2}` |
| matrices, `\begin{...}` | one `d.text()` per row, or a table of shapes |
| accents: `\hat \bar \vec \tilde \dot` | a prime or a subscript: `y'`, `y_{\mathrm{est}}` |
| `\mathcal`, `\mathfrak` | `\mathbf` or a Greek letter |
| stretchy delimiters | plain `( )`, `[ ]`, `\langle \rangle` |

## Mixing math and text

Math and markup combine freely in one label, and lines break only outside math:

```python
d.text(
    "Valid$(a_i, I)$ = Provenance$(a_i, I) \\land$ Capability$(a_i, I)$\n"
    "*holds for every action* $a_i$",
    size=14, align="center",
)
```

Label width is measured from the same outlines that are drawn, so a shape grows to fit a formula just as it does for plain text.
