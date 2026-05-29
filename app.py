from rag_pipeline.vector_store import build_vector_store,load_vector_store
# from rag_pipeline.retriever import retriever
# from rag_pipeline.compressor import compress
# from rag_pipeline.generator import generator
# from rag_pipeline.reranker import rerank
from memory_store import (
    load_memory, save_memory,
      add_message, get_history,
      clear_scratchpad)
from rag_pipeline.embeddings import get_embedding_model
# from intent_router import classify_intent,rewrite_query
# from order_services import start_order, handle_order_submission,check_order_status
import time
from agent.agent import run_react_agent
# ORDER_TIMEOUT = 600  # 10 minutes

def process_message(user_id, query):
    try:
        session = load_memory(user_id)
        history = get_history(session)

        # ReAct agent hnadles everything
        response = run_react_agent(
            user_query = query,
            user_id = user_id,
            history = history            
        ) 

        #save memory
        add_message(session, "user", query)
        add_message(session, "assistant", response)
        clear_scratchpad(session)
        save_memory(user_id, session)

        return response
    
    except Exception as e:
        print(f"[PIPELINE ERROR] {e}")
        return "Something went wrong. Please try again."

if __name__ == '__main__':
    print('Loading embedding model')
    get_embedding_model()
    print('Embedding model loaded.')

    index, documents = load_vector_store()
    if index is None:
        print('Building vector store...')
        build_vector_store()

    print('Agent is online. Type (exit) to quit.\n')

    while True:
        user_input = input('User: ')
        if user_input == 'exit':
            break
        response = process_message('test_user', user_input)
        print(f'Agent: {response}')
        print('\n' + '-'*50 + '\n')


# def process_message(user_id,query):
#     try:
    
#         session = load_memory(user_id)
#         if session['order']['state'] != 'idle':
#             last_update = session['order'].get('last_update')
#             if last_update and time.time() - last_update> ORDER_TIMEOUT:
#                 session['order'] = {
#                     'state': 'idle',
#                     'data': {},
#                     'last_update': None
#                 }
#                 save_memory(user_id,session)
#         history = session['history']

#         if session['order']['state'] in ['awaiting_template','awaiting_confirmation']:
#             response = handle_order_submission(query,user_id)
#             session = load_memory(user_id)
        
#         else:
#             intent = classify_intent(query,history,user_id)
#             response = "I'm sorry, I couldn't understand that."

#             if intent == 'product_query':

#                 domain = 'product'
#                 index, documents = load_vector_store()

#                 if index is None:
#                     index,documents = build_vector_store()

#                 if not history:
#                     rewritten_query = query
#                 else:
#                     rewritten_query = rewrite_query(query,history,user_id)

#                 retrieved_chunks = retriever(
#                     rewritten_query,
#                     index,
#                     documents,
#                     domain = domain
#                     )

#                 if not retrieved_chunks:
#                     response = 'could you clarify your request'
#                 else:    
#                     try:    
#                         reranked_chunks = rerank(
#                             rewritten_query,
#                             retrieved_chunks,
#                             top_k =3
#                             )
#                     except Exception as e:
#                         print(f"[RERANK ERROR] {e}")
#                         reranked_chunks = retrieved_chunks[:3]

#                     compressed_context = compress(
#                         rewritten_query,
#                         reranked_chunks,
#                         user_id
#                         )
#                     response = generator(
#                         query,
#                         compressed_context,
#                         history,
#                         user_id
#                         )
        
#             elif intent == 'place_order':
#                 response = start_order(user_id)
#                 session = load_memory(user_id)

#             elif intent == 'order_status':
#                 response = check_order_status(query,user_id)
        
#         # Update and save memory
#         session['history'].append({"role": "user", "content": query})
#         session['history'].append({"role": "assistant", "content": response})
#         save_memory(user_id, session)

#         return response

#     except Exception as e:
#         print(f"[PIPELINE ERROR] {e}")
#         return "Something went wrong. Please try again."

# if __name__=='__main__':
#     print('Loading embedding model')
#     get_embedding_model()
#     print('Embedding model Loaded ....')
#     print('Agent is online ')
#     print('type (exit) to terminate chat')
#     while True:
#         user_input = input('user:')
#         if user_input =='exit':
#             break
#         response = process_message('test_user',user_input)
#         print('Agent: ',response)
#         print('\n'+ '-'*50 + '\n')