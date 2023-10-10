#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import sys
import signal
import typer
from typing_extensions import Annotated
from gpt4all import GPT4All

VERSION = f'v0.0.1'

app = typer.Typer()


def signal_handler(sig, frame):
    print("\n\nExiting...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


@app.command()
def repl(
        model: Annotated[
            str,
            typer.Option("--model", "-m",
                         help="Model to use for gpt",
                         ),
        ] = "",
        n_threads: Annotated[
            int,
            typer.Option("--threads", "-t",
                         help="Number of threads to use for gpt",
                         ),
        ] = None,
        device: Annotated[
            str,
            typer.Option("--device", "-d",
                         help="Device to use for gpt, cpu or gpu",
                         ),
        ] = "cpu",
):
    if not model:
        print("Please specify a model to use with --model")
        sys.exit(1)

    gpt4all_instance = GPT4All(
        model,
        allow_download=False,
        device=device,
    )

    if n_threads is not None:
        print(f"\nAdjusted: {gpt4all_instance.model.thread_count()}")
        gpt4all_instance.model.set_thread_count(n_threads)

    print(f"\nUsing {gpt4all_instance.model.thread_count()} threads")

    while True:
        print(f"# Start chatting with the assistant, type /help for special commands", flush=True)
        session_loop(gpt4all_instance)


def session_loop(gpt4all_instance: GPT4All):
    with gpt4all_instance.chat_session():
        while True:
            message = input("$> ")

            # if empty message, ignore
            if not message:
                continue

            output_file = None

            if message.startswith('/'):
                # Check if special command and take action
                if message.startswith('/reset'):
                    # Clear screen
                    print("\033c", end='')
                    break
                if message.startswith('/exit'):
                    sys.exit()

                if message.startswith('/help'):
                    print("Special commands:\n"
                          "/help\n"
                          "/reset\n"
                          "/exit\n"
                          "/io <input-file> <output-file> [prompt...]\n"
                          )
                    continue

                if message.startswith('/io'):
                    args = message.split(' ', 4)
                    if len(args) < 3:
                        print("Usage: /io <input-file> <output-file> [prompt...]")
                        continue
                    with open(args[1], 'r') as f:
                        message = f.read()

                    if len(args) > 3:
                        message += args[3] + ' ' + message
                    output_file = args[2]

            response_generator = gpt4all_instance.generate(
                message,
                max_tokens=200,
                temp=0.9,
                top_k=40,
                top_p=0.9,
                repeat_penalty=1.1,
                repeat_last_n=64,
                n_batch=9,
                streaming=True,
            )
            response = io.StringIO()

            if output_file is not None:
                with open(output_file, 'w') as f:
                    for token in response_generator:
                        f.write(token)
                        response.write(token)
            else:
                for token in response_generator:
                    print(token, end='', flush=True)
                    response.write(token)

            output = response.getvalue()

            response.close()

            response_message = {'role': 'assistant', 'content': output}
            gpt4all_instance.current_chat_session.append(response_message)
            print()


@app.command()
def version():
    print(f"{VERSION}")


if __name__ == "__main__":
    app()
