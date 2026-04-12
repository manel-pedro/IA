# Self-Driving Rides Optimization (Google Hash Code)

Este projeto foi desenvolvido no âmbito da Unidade Curricular de Inteligência Artificial. O sistema resolve o problema de escalonamento de frotas de veículos elétricos numa grelha urbana, focando-se na maximização da pontuação total (distância percorrida + bónus de pontualidade) através de múltiplas abordagens algorítmicas.

## Autores
* **Gonçalo Santos**
* **João Ferreira**
* **Manuel Pedro**

---

## Requisitos e Instalação

O programa foi desenvolvido inteiramente em **Python 3**. 

### Pré-requisitos
* **Python 3.8 ou superior** instalado.
* **Tkinter:** Geralmente já incluído na instalação padrão do Python.
    * *Linux:* `sudo apt-get install python3-tk`
    * *Windows/macOS:* Já incluído no instalador oficial (python.org).

### Como Executar
Navegue até à pasta raiz do projeto através do terminal e execute:
```bash
python3 main.py
```


## Modos de Funcionamento

Ao iniciar, o programa apresenta um menu interativo com duas opções principais:
### 1. Modo Terminal (Processamento Individual)

Ideal para resolver datasets massivos de forma rápida e eficiente.

O utilizador:
    
- Seleciona um ficheiro de entrada da pasta input/.

- Escolhe o algoritmo de otimização pretendido.

- O sistema gera automaticamente o ficheiro de submissão na pasta output/.

### 2. Interface Gráfica (Visualizador)

Uma ferramenta de validação visual que permite observar os steps do problema e a movimentação dos veículos em tempo real. 


## Modo Benchmark (Análise Comparativa)

A opção recomendada para testes científicos e comparação de performance, que executa todos os algoritmos implementados sobre todos os ficheiros presentes na pasta input/.

No final, gera uma ficheiro .csv detalhando o Score obtido e o Tempo de Execução (em segundos) de cada método.

Para o usar, é só ir até ao terminal e correr:

```bash
python3 benchmark.py
```