# Jogo da memória multiplayer
O objetivo deste projeto é a integração de um sistema multiplayer baseado em comunicação via socket utilizando a API Socket da biblioteca padrão Python

## Base
Inicialmente o jogo foi escrito em python 2 e foi portado para python 3
Port de python2 para python3 foi feito em conjunto com Maximillian Harrisson

## Multiplayer
O sistema de conexão funciona com no protocolo de Sockets usando a comunicação por TCP em IPv4
Foi decidido projetar a modularização com o cliente fino e o servidor tendo toda a responsabilidade de lógica
A divisão de trabalho se deu por 2 grupos, um desenvolvendo o back-end e outro o front-ent (servidor e cliente)

## Server
A equipe responsável pelo servidor é composta por: Rodrigo Mota e Pedro Lanzarini
O servidor então se é aberto em uma porta pré definida e customizável, (Padrão 30000)
O processo define por input a quantidade de jogadores e o tamanho do tabuleiro de jogo, após isso espera a conexão dos jogadores e inicia a partida
Toda a comunicação é feita via mensagens encabeçadas pelo tamanho da mensagem num protocolo de comunicação de fixed header size, todo dado enviado é serializado via Pickle, causando uma dependência do cliente também ser em Python, isso foi uma escolha arbitrária e possivelmente será refeito no futuro.

## Cliente
A equipe responsável pelo cliente é composta por: Maximillian Harrisson e Isadora Pacheco
O cliente se conecta no servidor via IP e porta e trabalha recebendo um fluxo de mensagens separadas por flags, cada flag define o tipo de mensagem que será recebido e trata a mensagem de acordo, seja exibindo o dado no console ou enviando input de volta ao servidor.
