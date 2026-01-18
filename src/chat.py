from search import search_prompt

question="me traga tudo sobre a epresa Cobalto Energia Indústria que consta nesse documento"

##question="Qual é a capital da França?"

##question="Quantos clientes temos em 2024?"

##question="Você acha isso bom ou ruim?"



def main():
    chain = search_prompt(question)

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return
    
    pass

if __name__ == "__main__":
    main()