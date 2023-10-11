import ast
import asyncio
import collections
import logging
import sys


def main():
    asyncio.run(amain())


async def amain():
    storage = collections.deque()
    # Ignore the header, number of test cases
    sys.stdin.readline()
    await consume_input(storage=storage)
    await print_output(storage=storage)


def forever(func):
    """
    Call `func` repeatedly, until an exception is raised.

    Since Python does not support tail recursion,
    and the default stack depth is 1000,
    and it would be cool to support arbitrary number of test cases,
    let's chain async tasks to execute useful code repeatedly.
    """
    finished = asyncio.Event()
    kwargs = {}

    async def dummy():
        pass

    async def start(**kw):
        kwargs.update(kw)
        asyncio.ensure_future(dummy()).add_done_callback(done)
        await finished.wait()

    def done(prev):
        if prev.exception():
            finished.set()
        else:
            asyncio.ensure_future(func(**kwargs)).add_done_callback(done)

    return start


@forever
async def consume_input(*, storage):
    """Consumer standard input, one line at a time without using loops"""
    # Ignore the sub-header, number of integers in a test
    sys.stdin.readline()
    line = sys.stdin.readline()
    # Stop on EOF
    assert line
    storage.append(positive_square_sum(line))


@forever
async def print_output(*, storage):
    """Print out accumulated results, without using loops"""
    # Side-effect: stop when storage is empty
    print(storage.popleft())


def positive_square_sum(s: str) -> int:
    """
    Compute the sum of squares of space-separated integers, ignoring negative integers, without using loops.

    Let's abuse AST visitor iteration to process arbitrarily many numbers per line.
    """
    result = 0

    class Emitter(ast.NodeVisitor):
        def visit_UnaryOp(self, node: ast.UnaryOp):
            """Ignore negative numbers"""
            return

        def visit_Constant(self, node: ast.Constant):
            """Collect squares of remaining numbers"""
            nonlocal result
            result += node.value**2

    Emitter().visit(ast.parse(s.replace(" ", ",")))
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()


def test_positive_square_sum():
    assert positive_square_sum("") == 0
    assert positive_square_sum("\n") == 0
    assert positive_square_sum("0") == 0
    assert positive_square_sum("-1") == 0
    assert positive_square_sum("1 1\n") == 2
    assert positive_square_sum("3 -1 1 14") == 206
    assert positive_square_sum("9 6 -53 32 16") == 1397
